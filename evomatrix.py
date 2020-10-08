import Tkinter
import sched, time, random, math

g_cols, g_rows = 50,50
g_alive   = [[False for x in range(g_cols)] for y in range(g_rows)]
g_energy  = [[0 for x in range(g_cols)] for y in range(g_rows)]
g_motion  = [[0.5 for x in range(g_cols)] for y in range(g_rows)]
g_diet    = [[0.8 for x in range(g_cols)] for y in range(g_rows)]
g_power   = [[0.5 for x in range(g_cols)] for y in range(g_rows)]
tps = 30
fps = 30

root = Tkinter.Tk()

g_alive[int(g_cols/2)][int(g_rows/2)] = True
g_energy[int(g_cols/2)][int(g_rows/2)] = 0.8
NEIGHBOURLIST = [[+1,0],[+1,+1],[0,+1],[-1,+1],[-1,0],[-1,-1],[0,-1],[+1,-1]]

def floattohex(input): #helper function to map numbers from 0 to 1 to hex values from 1 to f
    return str(hex(int(16*input-1)).split('x')[-1])

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
                trim = (cs-(cs*math.sqrt(g_energy[x][y])))/2
                cellcolor = '#' + floattohex(g_power[x][y]) + floattohex(g_diet[x][y]) + floattohex(g_motion[x][y])
                c.create_rectangle(x*cs+trim,y*cs+trim,x*cs+cs-trim,y*cs+cs-trim,fill=cellcolor, tag='cell')
    root.after(1000/fps, draw_grid)

def step_grid(): #calculations for behavior of every cell
    for x in range(0, g_cols):
        for y in range(0, g_rows):
            if g_alive[x][y]:
                #get energy from the sun
                g_energy[x][y] += 0.1 * (g_diet[x][y])
                #lose energy
                g_energy[x][y] -= (0.03+0.02*g_power[x][y])
                #movement
                if g_energy[x][y] > 0.2:
                    pick = random.choice(NEIGHBOURLIST)
                    ox = int(x+pick[0]) % g_cols
                    oy = int(y+pick[1]) % g_rows
                    if random.random() < g_motion[x][y]:
                        if g_alive[ox][oy] == False:
                            g_energy[ox][oy] = min(1,(g_energy[x][y] - 0.03))
                            g_diet[ox][oy] = g_diet[x][y]
                            g_motion[ox][oy] = g_motion[x][y]
                            g_power[ox][oy] = g_power[x][y]
                            g_alive[x][y] = False
                            g_alive[ox][oy] = True
                #fight and eat if moving to another cell
                        else:
                            if g_energy[ox][oy] > 0.8*g_power[x][y]: 
                                g_energy[ox][oy] -= 0.8*g_power[x][y]
                                g_energy[x][y] += 0.8*g_power[x][y] * (1-g_diet[x][y])
                            else:
                                g_energy[x][y] += g_energy[ox][oy] * (1-g_diet[x][y])
                                g_alive[ox][oy] = False
                            if g_alive[ox][oy] == True: #other fights back
                                if g_energy[x][y] > 0.8*g_power[ox][oy]:
                                    g_energy[x][y] -= 0.8*g_power[ox][oy]
                                    g_energy[ox][oy] += 0.8*g_power[ox][oy] * (1-g_diet[ox][oy])
                                else:
                                    g_energy[ox][oy] += g_energy[x][y] * (1-g_diet[ox][oy])
                                    g_alive[x][y] = False
                                if g_energy[ox][oy] > 1:
                                    g_energy[ox][oy] = 1
                #reproduce
                    if g_energy[x][y] > 0.9:
                        pick = random.choice(NEIGHBOURLIST)
                        ox = int(x+pick[0]) % g_cols
                        oy = int(y+pick[1]) % g_rows
                        if g_alive[ox][oy] == False:
                            g_alive[ox][oy] = True
                            g_energy[ox][oy] = 0.3
                            g_diet[ox][oy]   = mutate(g_diet[x][y])
                            g_motion[ox][oy] = mutate(g_motion[x][y])
                            g_power[ox][oy]  = mutate(g_power[x][y])                   
                            g_energy[x][y] -= 0.3
                #death
                if g_energy[x][y] > 1:
                    g_energy[x][y] = 1
                if g_energy[x][y] < 0:
                    g_alive[x][y] = False
    root.after(1000/tps, step_grid)

root.after(0, step_grid)
root.after(0, draw_grid)

c = Tkinter.Canvas(root, height=1000, width=1000, bg='#000')
c.pack(fill=Tkinter.BOTH, expand=True)
c.bind(draw_grid)
root.mainloop()