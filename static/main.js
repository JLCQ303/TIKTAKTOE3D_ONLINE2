const socket = io();
let ROOM=null, MY_ROLE=null;
const tablero=document.getElementById('tablero');
const labelRole=document.getElementById('labelRole');
const turnoLabel=document.getElementById('turno');
document.getElementById('btnJoin').onclick=()=>{
 const code=document.getElementById('room').value.trim();
 if(!code){alert('Ingresa código');return;}
 ROOM=code; socket.emit('join',{room:ROOM});
};
document.getElementById('btnRestart').onclick=()=>{
 if(!ROOM){alert('Ingresa sala');return;}
 socket.emit('restart',{room:ROOM});
};
for(let r=0;r<16;r++){
 for(let c=0;c<16;c++){
  let ph=document.createElement('div');
  ph.className='placeholder'; tablero.appendChild(ph);
 }}
for(let z=3;z>=0;z--){
 for(let y=0;y<4;y++){
  for(let x=0;x<4;x++){
   const cell=document.createElement('div');
   cell.className='celda';
   const row=y+z*4+1, col=x+(3-z)*4+1;
   cell.style.gridRow=row; cell.style.gridColumn=col;
   const idx=z*16+y*4+x; cell.id='c'+idx;
   cell.onclick=()=>{
    if(!ROOM){alert('Entra sala');return;}
    if(!MY_ROLE || MY_ROLE==='SPECTATOR'){alert('Espectador');return;}
    socket.emit('play',{room:ROOM,index:idx});
   };
   tablero.appendChild(cell);
 }}}
socket.on('joined',d=>{
 if(!d.ok){alert(d.error);return;}
 MY_ROLE=d.role; labelRole.innerText='Tu rol: '+MY_ROLE;
 if(d.state) render(d.state);
});
socket.on('state',d=>render(d));
socket.on('finished',d=>{
 if(d.indices){d.indices.forEach(i=>{
   const c=document.getElementById('c'+i);
   if(c)c.classList.add('winner');
 });}
 alert('Ganador: Jugador '+d.winner);
});
function render(state){
 turnoLabel.innerText=state.fin?'Juego terminado':'Turno jugador '+(state.turno+1);
 const arr=state.jugadas;
 for(let z=0;z<4;z++)for(let y=0;y<4;y++)for(let x=0;x<4;x++){
  const idx=z*16+y*4+x, v=arr[z][y][x], el=document.getElementById('c'+idx);
  el.innerText=v==-1?'X':v==1?'O':''; el.className='celda';
  if(v==-1)el.classList.add('blue'); if(v==1)el.classList.add('red');
 }
}
