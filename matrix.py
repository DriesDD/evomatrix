#WIP. The goal here is to rewrite the code with numpy matrices for better performance
import Tkinter
import random, math
import numpy as np
from time import perf_counter


#create matrices
M_COLS, M_ROWS = 32,32
g_alive   = np.zeros((M_COLS,M_ROWS),dtype=np.bool)
g_energy  = np.zeros((M_COLS,M_ROWS),dtype=np.int8)
g_power   = np.zeros((M_COLS,M_ROWS),dtype=np.int8)
g_diet    = np.zeros((M_COLS,M_ROWS),dtype=np.int8)
g_motion  = np.zeros((M_COLS,M_ROWS),dtype=np.int8)
#x and y are the planar positions, while z are the properties energy,power,diet,motion
g_cells   = np.zeros((M_COLS,M_ROWS,4),dtype=np.int8)

TPS = 200
FPS = 200

MUTATION_RATE = 1
DISRUPTION_RATE = 0.1
AUTOTROPH_RATE = 9
ENERGYLOSS_RATE = 8
MOVEMENT_COST = 6
ACTIVE_TRESHOLD = 20
FIGHTING_MODIFIER = 60
REPRODUCE_TRESHOLD = 80
OFFSPRING_ENERGY = 40

root = Tkinter.Tk()

g_alive[int(M_COLS/2)][int(M_ROWS/2)] = True
g_energy[int(M_COLS/2)][int(M_ROWS/2)] = 80
g_motion[int(M_COLS/2)][int(M_ROWS/2)] = 50
g_diet[int(M_COLS/2)][int(M_ROWS/2)] = 80
g_power[int(M_COLS/2)][int(M_ROWS/2)] = 50

NEIGHBOURLIST = [[+1,0],[+1,+1],[0,+1],[-1,+1],[-1,0],[-1,-1],[0,-1],[+1,-1]]

def curve(num): # helper function to map int8s from 0 to 100 from a linear to a curve
    return (100*math.cos(math.pi+math.pi*num/100)/2 + 0.5)

def floattohex(input): #helper function to map int8s from 0 to 100 to hex values from 1 to f
    return str(hex(int(16*(input/100)-1)).split('x')[-1])

def mutate(n):
    s = MUTATION_RATE
    if random.random() > 1-5*s:
        return max(0, min(100, random.gauss(n,s*10)))
    return max(0, min(100, random.gauss(n,s)))

def draw_grid(): #draws every cell
    w = c.winfo_width()
    h = c.winfo_height()
    cs = min(w/M_COLS,h/M_ROWS)
    c.delete('cell')
    c.delete('dot')
    c.delete('line')
    length = 300
    cos30 = math.cos(math.pi/6)
    sin30 = math.sin(math.pi/6)
    centerx = cs*M_COLS+length/2
    centery = h/2
    c.create_line(centerx,centery,centerx,centery-length/2,fill="grey20",tag='line')
    c.create_line(centerx,centery,centerx+cos30*length/2,centery+sin30*length/2,fill="grey20",tag='line')
    c.create_line(centerx,centery,centerx-cos30*length/2,centery+sin30*length/2,fill="grey20",tag='line')

    c.create_line(centerx-cos30*length/2,centery+sin30*length/2+1,centerx,centery+length/2,fill="red",tag='line')
    c.create_line(centerx+cos30*length/2,centery+sin30*length/2,centerx,centery+length/2,fill="green",tag='line')

    c.create_line(centerx-cos30*length/2,centery+sin30*length/2,centerx-cos30*length/2,centery-sin30*length/2,fill="red",tag='line')
    c.create_line(centerx+cos30*length/2,centery+sin30*length/2,centerx+cos30*length/2,centery-sin30*length/2,fill="green",tag='line')

    c.create_line(centerx-cos30*length/2,centery-sin30*length/2,centerx,centery-length/2,fill="blue",tag='line')
    c.create_line(centerx+cos30*length/2,centery-sin30*length/2,centerx,centery-length/2,fill="blue",tag='line')

    start_time = perf_counter()
    for x in range(0, M_COLS):
        for y in range(0, M_ROWS):
            if g_alive[x][y] == True:
                trim = (cs-(cs*math.sqrt(max(0,g_energy[x][y]))))/2
                cellcolor = '#' + floattohex(g_power[x][y]) + floattohex(g_diet[x][y]) + floattohex(g_motion[x][y])
                
                c.create_rectangle(x*cs+trim,y*cs+trim,x*cs+cs-trim,y*cs+cs-trim,fill=cellcolor, outline='', tag='cell')
                
                red = g_power[x][y]*length/2
                green = g_diet[x][y]*length/2
                blue = g_motion[x][y]*length/2
                
                yshift = -blue+green/2+red/2
                xshift = green*cos30-red*cos30

                c.create_rectangle(centerx+xshift-1,centery+yshift-1,centerx+xshift+1,centery+yshift+1,fill=cellcolor, outline='', tag='dot')

    root.after(1000/fps, draw_grid)
    end_time = perf_counter()
    print(f"Draw Time: {end_time - start_time:0.6f}" )

def step_grid(stepcount): #calculations for behavior of every cell
    start_time = perf_counter()
    for x in range(0, M_COLS):
        for y in range(0, M_ROWS):
            if g_alive[x][y]:
                #get energy from the sun
                g_energy[x][y] += AUTOTROPH_RATE * curve(g_diet[x][y])
                #lose energy
                g_energy[x][y] -= ENERGYLOSS_RATE * curve(g_power[x][y])
                #die from an accident
                if random.random() > 1-DISRUPTION_RATE:
                    g_alive[x][y] = False
                    for each in NEIGHBOURLIST:
                        g_alive[(x+each[0]) % M_COLS][(y+each[1]) % M_ROWS] = False
                #movement
                if g_energy[x][y] > ACTIVE_TRESHOLD:
                    pick = random.choice(NEIGHBOURLIST)
                    ox = int(x+pick[0]) % M_COLS
                    oy = int(y+pick[1]) % M_ROWS
                    if random.random() < curve(g_motion[x][y]):
                        g_energy[x][y] -= MOVEMENT_COST
                        if g_alive[ox][oy] == False:
                            g_energy[ox][oy] = g_energy[x][y]
                            g_diet[ox][oy] = g_diet[x][y]
                            g_motion[ox][oy] = g_motion[x][y]
                            g_power[ox][oy] = g_power[x][y]
                            g_alive[x][y] = False
                            g_alive[ox][oy] = True
                #fight and eat if moving to a live cell
                        else:
                            if curve(g_power[x][y]) > curve(g_power[ox][oy])*FIGHTING_MODIFIER:
                                if g_energy[ox][oy] < curve(g_power[x][y]) - FIGHTING_MODIFIER*curve(g_power[ox][oy]):
                                    g_alive[ox][oy] = False
                                g_energy[ox][oy] -= curve(g_power[x][y]) - FIGHTING_MODIFIER*curve(g_power[ox][oy])
                                g_energy[x][y] += (curve(g_power[x][y]) - FIGHTING_MODIFIER*curve(g_power[ox][oy])) * (1-curve(g_diet[x][y]))
                #reproduce
                    if g_energy[x][y] > REPRODUCE_TRESHOLD:
                        pick = random.choice(NEIGHBOURLIST)
                        ox = int(x+pick[0]) % M_COLS
                        oy = int(y+pick[1]) % M_ROWS
                        if g_alive[ox][oy] == False:
                            g_alive[ox][oy] = True
                            g_energy[ox][oy] = OFFSPRING_ENERGY
                            g_diet[ox][oy]   = mutate(g_diet[x][y])
                            g_motion[ox][oy] = mutate(g_motion[x][y])
                            g_power[ox][oy]  = mutate(g_power[x][y])             
                            g_energy[x][y] -= OFFSPRING_ENERGY
                #death
                if g_energy[x][y] > 1:
                    g_energy[x][y] = 1
                if g_energy[x][y] <= 0:
                    g_alive[x][y] = False
    if stepcount/1000 % 1 == 0:
        print(str(stepcount) +' ticks.')
        
    end_time = perf_counter()
    print(f"Step Time: {end_time - start_time:0.6f}" )
    root.after(1000/tps, step_grid, stepcount+1)

root.after(0, step_grid, 0.0)
root.after(0, draw_grid)

c = Tkinter.Canvas(root, height=1000, width=1000, bg='#000')
c.pack(fill=Tkinter.BOTH, expand=True)
c.bind(draw_grid)
root.mainloop()
