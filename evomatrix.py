import Tkinter
import sched, time, random, math

g_cols, g_rows = 50,50
g_alive   = [[False for x in range(g_cols)] for y in range(g_rows)]
g_energy  = [[0 for x in range(g_cols)] for y in range(g_rows)]
g_motion  = [[0.2 for x in range(g_cols)] for y in range(g_rows)]
g_diet    = [[0.8 for x in range(g_cols)] for y in range(g_rows)]
g_power   = [[0.2 for x in range(g_cols)] for y in range(g_rows)]
tps = 100
fps = 3

root = Tkinter.Tk()

g_alive[int(g_cols/2)][int(g_rows/2)] = True
g_energy[int(g_cols/2)][int(g_rows/2)] = 0.8
NEIGHBOURLIST = [[+1,0],[+1,+1],[0,+1],[-1,+1],[-1,0],[-1,-1],[0,-1],[+1,-1]]

def curve(num): # helper function to map floats from 0 to 1 from a linear to a curve
    return (math.cos(math.pi+math.pi*num)/2 + 0.5)

def floattohex(input): #helper function to map numbers from 0 to 1 to hex values from 1 to f
    return str(hex(int(16*input-1)).split('x')[-1])

def mutate(n,s):
    if random.random() > 0.95:
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

    root.after(1000/fps, draw_grid)

def step_grid(countdown): #calculations for behavior of every cell
    for x in range(0, g_cols):
        for y in range(0, g_rows):
            if g_alive[x][y]:
                #get energy from the sun
                g_energy[x][y] += 0.1 * curve(g_diet[x][y])
                #lose energy
                g_energy[x][y] -= 0.08 * curve(g_power[x][y])
                #die from an accident
                if random.random() > 0.998:
                    g_alive[x][y] = False
                #movement
                if g_energy[x][y] > 0.2:
                    pick = random.choice(NEIGHBOURLIST)
                    ox = int(x+pick[0]) % g_cols
                    oy = int(y+pick[1]) % g_rows
                    if random.random() < curve(g_motion[x][y]):
                        g_energy[x][y] -= 0.04
                        if g_alive[ox][oy] == False:
                            g_energy[ox][oy] = g_energy[x][y]
                            g_diet[ox][oy] = g_diet[x][y]
                            g_motion[ox][oy] = g_motion[x][y]
                            g_power[ox][oy] = g_power[x][y]
                            g_alive[x][y] = False
                            g_alive[ox][oy] = True
                #fight and eat if moving to a live cell
                        else:
                            if curve(g_power[x][y]) > curve(g_power[ox][oy])*0.6:
                                if g_energy[ox][oy] < curve(g_power[x][y]) - 0.6*curve(g_power[ox][oy]):
                                    g_alive[ox][oy] = False
                                g_energy[ox][oy] -= curve(g_power[x][y]) - 0.6*curve(g_power[ox][oy])
                                g_energy[x][y] += (curve(g_power[x][y]) - 0.6*curve(g_power[ox][oy])) * (1-curve(g_diet[x][y]))                                    
                #reproduce
                    if g_energy[x][y] > 0.9:
                        pick = random.choice(NEIGHBOURLIST)
                        ox = int(x+pick[0]) % g_cols
                        oy = int(y+pick[1]) % g_rows
                        if g_alive[ox][oy] == False:
                            g_alive[ox][oy] = True
                            g_energy[ox][oy] = 0.3
                            g_diet[ox][oy]   = mutate(g_diet[x][y],0.01)
                            g_motion[ox][oy] = mutate(g_motion[x][y],0.01)
                            g_power[ox][oy]  = mutate(g_power[x][y],0.01)             
                            g_energy[x][y] -= 0.3
                #death
                if g_energy[x][y] > 1:
                    g_energy[x][y] = 1
                if g_energy[x][y] <= 0:
                    g_alive[x][y] = False
    if countdown/1000 % 1 == 0:
        print(str(countdown) +' steps to go.')
    root.after(1000/tps, step_grid, countdown-1)

root.after(0, step_grid, 20000.0)
root.after(0, draw_grid)

c = Tkinter.Canvas(root, height=1000, width=1000, bg='#000')
c.pack(fill=Tkinter.BOTH, expand=True)
c.bind(draw_grid)
root.mainloop()