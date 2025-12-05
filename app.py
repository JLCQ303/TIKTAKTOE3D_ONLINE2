from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from logica import Juego3D
import threading

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

rooms = {}
lock = threading.Lock()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def on_join(data):
    room = data.get('room')
    if not room:
        emit('joined', {'ok': False, 'error': 'Sin codigo de sala'})
        return
    sid = request.sid
    join_room(room)
    with lock:
        if room not in rooms:
            rooms[room] = {'game': Juego3D(), 'players': {}, 'order': []}
        roominfo = rooms[room]
        players = roominfo['players']
        assigned = None
        if sid in players:
            assigned = players[sid]
        else:
            if len(players) < 2:
                assigned = 'X' if 'X' not in players.values() else 'O'
                players[sid] = assigned
                roominfo['order'].append(sid)
            else:
                assigned = 'SPECTATOR'
        state = roominfo['game'].exportar()
        emit('joined', {'ok': True, 'role': assigned, 'state': state}, to=sid)
        emit('players_update', {'players': list(players.values())}, to=room)

@socketio.on('play')
def on_play(data):
    room = data.get('room')
    idx = data.get('index')
    sid = request.sid
    if not room or idx is None:
        return
    with lock:
        if room not in rooms:
            return
        roominfo = rooms[room]
        players = roominfo['players']
        role = players.get(sid)
        game = roominfo['game']
        if game.g:
            emit('error', {'msg': 'Juego terminado'}, to=sid)
            return
        if role not in ('X','O'):
            emit('error', {'msg': 'No eres jugador'}, to=sid)
            return
        expected_role = 'X' if game.jugador==0 else 'O'
        if role != expected_role:
            emit('error', {'msg': 'No es tu turno'}, to=sid)
            return
        res = game.jugar(idx)
        emit('state', game.exportar(), to=room)
        if res.get('msg') == 'gano':
            emit('finished', {'winner': res.get('jugador'), 'indices': res.get('indices')}, to=room)

@socketio.on('restart')
def on_restart(data):
    room = data.get('room')
    with lock:
        if room in rooms:
            rooms[room]['game'].reiniciar()
            emit('state', rooms[room]['game'].exportar(), to=room)

@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    with lock:
        empty=[]
        for room,info in rooms.items():
            if sid in info['players']:
                del info['players'][sid]
                if sid in info['order']:
                    info['order'].remove(sid)
                emit('players_update', {'players': list(info['players'].values())}, to=room)
            if not info['players']:
                empty.append(room)
        for r in empty:
            del rooms[r]

if __name__=='__main__':
    socketio.run(app,host='0.0.0.0',port=5000,debug=True)
