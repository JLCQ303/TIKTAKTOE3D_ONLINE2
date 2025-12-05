class Juego3D:
    def __init__(self):
        self.jugadas = [[[0]*4 for _ in range(4)] for _ in range(4)]
        self.jugador = 0
        self.g = 0
        self.C = [
            [1,1,0],[1,0,1],[0,1,1],[1,0,0],[1,-1,0],
            [0,0,1],[-1,0,1],[0,1,0],[0,1,-1],[0,-1,-1],
            [0,-1,0],[0,0,-1],[0,0,0]
        ]

    def indices(self, i):
        Z = i // 16
        y = i % 16
        Y = y // 4
        X = y % 4
        return X, Y, Z

    def jugar(self, i):
        if self.g:
            return {'msg':'fin'}
        X,Y,Z = self.indices(i)
        if self.jugadas[Z][Y][X]!=0:
            return {'msg':'invalida'}
        placed = 'X' if self.jugador==0 else 'O'
        self.jugadas[Z][Y][X] = -1 if self.jugador==0 else 1
        for j in range(13):
            win = self.jugada_13_indices(j,X,Y,Z)
            if win:
                self.g=1
                return {'msg':'gano','jugador':self.jugador+1,'placed':placed,'indices':win}
        self.jugador = 1-self.jugador
        return {'msg':'ok','jugador':self.jugador+1,'placed':placed}

    def jugada_13_indices(self,c,X,Y,Z):
        tz,ty,tx = self.C[c]
        s=0
        coords=[]
        for i in range(4):
            z = Z if tz>0 else (3-i if tz==-1 else i)
            y = Y if ty>0 else (3-i if ty==-1 else i)
            x = X if tx>0 else (3-i if tx==-1 else i)
            s+= self.jugadas[z][y][x]
            coords.append((x,y,z))
        if abs(s)==4:
            return [z*16+y*4+x for (x,y,z) in coords]
        return []

    def reiniciar(self):
        self.__init__()

    def exportar(self):
        return {'jugadas':self.jugadas,'turno':self.jugador,'fin':self.g}
