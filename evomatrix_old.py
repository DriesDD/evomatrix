import Tkinter
import random, math, time

g_cols, g_rows = 32,32
g_alive   = [[False for x in range(g_cols)] for y in range(g_rows)]
g_energy  = [[0 for x in range(g_cols)] for y in range(g_rows)]
g_motion  = [[0.3 for x in range(g_cols)] for y in range(g_rows)]
g_diet    = [[0.4 for x in range(g_cols)] for y in range(g_rows)]
g_power   = [[0.2 for x in range(g_cols)] for y in range(g_rows)]
tps = 200
fps = 200

MUTATION_RATE = 0.01
DISRUPTION_RATE = 0.0001
AUTOTROPH_RATE = 0.07
ENERGYLOSS_RATE = 0.035
MOVEMENT_COST = 0.048
ACTIVE_TRESHOLD = 0.2
FIGHTING_MODIFIER = 0.6
REPRODUCE_TRESHOLD = 0.8
OFFSPRING_ENERGY = 0.4

root = Tkinter.Tk()

g_alive[int(g_cols/2)][int(g_rows/2)] = True
g_energy[int(g_cols/2)][int(g_rows/2)] = 0.8
NEIGHBOURLIST = [[+1,0],[+1,+1],[0,+1],[-1,+1],[-1,0],[-1,-1],[0,-1],[+1,-1]]

def curve(num): # helper function to map floats from 0 to 1 from a linear to a curve
    return (math.cos(math.pi+math.pi*num)/2 + 0.5)

def floattohex(input): #helper function to map numbers from 0 to 1 to hex values from 1 to f
    return str(hex(int(16*input-1)).split('x')[-1])

def mutate(n):
    s = MUTATION_RATE
    if random.random() > 1-5*s:
        return max(0, min(1, random.gauss(n,s*10)))
    return max(0, min(1, random.gauss(n,s)))

def draw_grid(): #draws every cell
    w = c.winfo_width()
    h = c.winfo_height()
    cs = min(w/g_cols,h/g_rows)
    c.delete('cell')
    c.delete('dot')
    c.delete('line')
    length = 300
    cos30 = math.cos(math.pi/6)
    sin30 = math.sin(math.pi/6)
    centerx = cs*g_cols+length/2
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

    start_time = time.time()
    for x in range(0, g_cols):
        for y in range(0, g_rows):
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
    end_time = time.time()
    print("Draw Time: " + str(end_time - start_time) )
    root.after(1000/fps, draw_grid)

def step_grid(stepcount): #calculations for behavior of every cell
    start_time = time.time()
    for x in range(0, g_cols):
        for y in range(0, g_rows):
            if g_alive[x][y]:
                #get energy from the sun
                g_energy[x][y] += AUTOTROPH_RATE * curve(g_diet[x][y])
                #lose energy
                g_energy[x][y] -= ENERGYLOSS_RATE * curve(g_power[x][y])
                #die from an accident
                if random.random() > 1-DISRUPTION_RATE:
                    g_alive[x][y] = False
                    for each in NEIGHBOURLIST:
                        g_alive[(x+each[0]) % g_cols][(y+each[1]) % g_rows] = False
                #movement
                if g_energy[x][y] > ACTIVE_TRESHOLD:
                    pick = random.choice(NEIGHBOURLIST)
                    ox = int(x+pick[0]) % g_cols
                    oy = int(y+pick[1]) % g_rows
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
                        ox = int(x+pick[0]) % g_cols
                        oy = int(y+pick[1]) % g_rows
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
    end_time = time.time()
    print("Step Time: " + str(end_time - start_time) )
    root.after(1000/tps, step_grid, stepcount+1)

root.after(0, step_grid, 0.0)
root.after(0, draw_grid)

c = Tkinter.Canvas(root, height=1000, width=1000, bg='#000')
c.pack(fill=Tkinter.BOTH, expand=True)
c.bind(draw_grid)
root.mainloop()
