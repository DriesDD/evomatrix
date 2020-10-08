import Tkinter as grid
import sched, time, random

g_cols, g_rows = 50,50
g_alive  = [[False for x in range(g_cols)] for y in range(g_rows)]
g_energy = [[0 for x in range(g_cols)] for y in range(g_rows)]
g_motion = [[0.2 for x in range(g_cols)] for y in range(g_rows)]
g_diet   = [[0 for x in range(g_cols)] for y in range(g_rows)]
g_power   = [[0 for x in range(g_cols)] for y in range(g_rows)]
tps = 100
fps = 10

root = grid.Tk()

g_alive[int(g_cols/2)][int(g_rows/2)] = True
g_energy[int(g_cols/2)][int(g_rows/2)] = 0.8
NEIGHBOURLIST = [[+1,0],[+1,+1],[0,+1],[-1,+1],[-1,0],[-1,-1],[0,-1],[+1,-1]]

def floattohex(input): #helper function to map numbers from 0 to 1 to hex values from 0 to f
    return str(hex(int(15*input)).split('x')[-1])

def mutate(n):
    return max(0, min(1, random.gauss(n,0.1)))

def draw_grid(): #draws every cell
    w = c.winfo_width()
    h = c.winfo_height()
    cs = min(w/g_cols,h/g_rows)
    c.delete('cell')
    for x in range(0, g_cols):
        for y in range(0, g_rows):
            if g_alive[x][y] == True:
                trim = (cs-(cs*pow(g_energy[x][y],2)))/2
                cellcolor = '#' + floattohex(g_power[x][y]) + floattohex(1-1*g_diet[x][y]) + floattohex(g_motion[x][y])
                c.create_rectangle(x*cs+trim,y*cs+trim,x*cs+cs-trim,y*cs+cs-trim,fill=cellcolor, tag='cell')
    root.after(1000/fps, draw_grid)


def step_grid(): #calculations for behavior of every cell
    for x in range(0, g_cols):
        for y in range(0, g_rows):
            if g_alive[x][y]:
                #growth and learning
                g_energy[x][y] += 0.1 * (1 - g_diet[x][y])
                #fighting each other (and moving)
                if g_energy[x][y] > 0.2:
                    pick = random.choice(NEIGHBOURLIST)
                    ox = int(x+pick[0]) % g_cols
                    oy = int(y+pick[1]) % g_rows
                    if random.random() < g_motion[x][y] ** 2:
                        if g_alive[ox][oy] == False: #movement
                            g_alive[ox][oy] = True
                            g_energy[ox][oy] = g_energy[x][y] - 0.1
                            g_diet[ox][oy] = g_diet[x][y]
                            g_motion[ox][oy] = g_motion[x][y]
                            g_alive[x][y] = False
                        else: #fight other
                            if g_energy[ox][oy] > g_power[x][y]:
                                g_energy[ox][oy] -= g_power[x][y]
                                g_energy[x][y] += g_power[x][y] * g_diet[x][y]
                            else:
                                g_energy[x][y] += g_energy[ox][oy] * g_diet[x][y]
                                g_alive[ox][oy] = False
                            if g_alive[ox][oy] == True: #other fights back
                                if g_energy[x][y] > g_power[ox][oy]:
                                    g_energy[x][y] -= g_power[ox][oy]
                                    g_energy[ox][oy] += g_power[ox][oy] * g_diet[ox][oy]
                                else:
                                    g_energy[ox][oy] += g_energy[x][y] * g_diet[ox][oy]
                                    g_alive[x][y] = False
                                if g_energy[ox][oy] > 1:
                                    g_energy[ox][oy] = 1
                #the miracle of birth
                    if g_energy[x][y] > 0.9:
                        if g_alive[int(x+pick[0]) % g_cols][int(y+pick[1]) % g_rows] == False:
                            g_alive[int(x+pick[0]) % g_cols][int(y+pick[1]) % g_rows] = True
                            g_energy[int(x+pick[0]) % g_cols][int(y+pick[1]) % g_rows] = 0.3
                            g_diet[int(x+pick[0]) % g_cols][int(y+pick[1]) % g_rows] = mutate(g_diet[x][y])
                            g_motion[int(x+pick[0]) % g_cols][int(y+pick[1]) % g_rows] = mutate(g_motion[x][y])
                            g_power[int(x+pick[0]) % g_cols][int(y+pick[1]) % g_rows] = mutate(g_power[x][y])                   
                            g_energy[x][y] -= 0.3
                #middle age
                #live organ transplants
                #the autumn years
                g_energy[x][y] -= 0.05-0.05*g_power[x][y]
                #death
                if g_energy[x][y] > 1:
                    g_energy[x][y] = 1
                if g_energy[x][y] < 0:
                    g_alive[x][y] = False
    root.after(1000/tps, step_grid)

root.after(0, step_grid)
root.after(0, draw_grid)

c = grid.Canvas(root, height=1000, width=1000, bg='#000')
c.pack(fill=grid.BOTH, expand=True)
c.bind(draw_grid)
root.mainloop()