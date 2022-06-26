import numpy as np
import pygame as pg
import math, random
from time import perf_counter

#constants (configurable)
GRID_SIZE = 64
SCALE = 20
FPS = 100
SPF = 1 #steps per frame
MUTATION_RATE = 0.01
DISRUPTION_RATE = 0.0001
AUTOTROPH_RATE = 9
ENERGYLOSS_RATE = 6
MOVEMENT_COST = 6
ACTIVE_TRESHOLD = 51
FIGHTING_MODIFIER = 0.9
REPRODUCE_TRESHOLD = 205
OFFSPRING_ENERGY = 102

#constants (not configurable)
SHAPE = (GRID_SIZE,GRID_SIZE)
DISP_SHAPE = (GRID_SIZE*SCALE,GRID_SIZE*SCALE)
NEIGHBOUR_LIST = [[+1,0],[+1,+1],[0,+1],[-1,+1],[-1,0],[-1,-1],[0,-1],[+1,-1]]
RNG = np.arange(0, 1, 0.01)
np.random.shuffle(RNG)
print(RNG)
rngi = 0

#create grids
g_alive = np.zeros(SHAPE, dtype=np.bool)
g_energy = np.zeros(SHAPE, dtype=np.uint8)
g_motion = np.zeros(SHAPE, dtype=np.uint8)
g_diet = np.zeros(SHAPE, dtype=np.uint8)
g_power = np.zeros(SHAPE, dtype=np.uint8)

#create first life
g_alive[(GRID_SIZE-1)//2,(GRID_SIZE-1)//2] = True
g_energy[(GRID_SIZE-1)//2,(GRID_SIZE-1)//2] = 128
g_motion[(GRID_SIZE-1)//2,(GRID_SIZE-1)//2] = 20
g_diet[(GRID_SIZE-1)//2,(GRID_SIZE-1)//2] = 154
g_power[(GRID_SIZE-1)//2,(GRID_SIZE-1)//2] = 77

#create canvas
pg.display.init()
pg.init()
clock = pg.time.Clock()
display = pg.display.set_mode(DISP_SHAPE)
surface = pg.Surface(SHAPE)

#helper functions
def curve(num): # helper function to map ints from 0 to 1 from a linear to a curve
    a = math.cos(math.pi+math.pi*(int(num)/256))/2 + 0.5 #cosine curve
    return a

def mutate(n): #mutates the value slightly, fat tail gauss curve
    s = MUTATION_RATE*256
    if RNG[rng_i()] > 1-5*MUTATION_RATE:
        return round(max(0, min(255, random.gauss(int(n),s*10))))
    return round(max(0, min(255, random.gauss(int(n),s))))

def rng_i():
    global rngi
    rngi += 1
    if rngi > 99:
        rngi = 0
    return rngi
#draw
def draw():
    start_time = perf_counter()
    #paint life on canvas
    pg.draw.rect(surface,'black',pg.Rect(0,0,GRID_SIZE,GRID_SIZE))
    for iy, ix in np.ndindex(SHAPE):
        if bool(g_alive[iy,ix]) == True:
            surface.set_at((iy,ix),pg.Color(int(g_power[iy,ix]),int(g_diet[iy,ix]),int(g_motion[iy,ix])))

    #refresh canvas
    scaledsurface = pg.transform.scale(surface,DISP_SHAPE)
    pg.Surface.blit(display,scaledsurface,(0,0))
    pg.display.flip()
    end_time = perf_counter()
    print(f"Draw Time: {end_time - start_time:0.6f}" )

#step
def step():
    start_time = perf_counter()
    #beforemovement, movement, movementloop, aftermovement,energy,chance,fight,motion,reproduce,actuallymoving,rand = 0,0,0,0,0,0,0,0,0,0,0
    for iy, ix in np.ndindex(SHAPE):
        if g_alive[iy,ix]:
            #part_counter = perf_counter()
            #subpart_counter = perf_counter()
            #get energy from the sun and lose energy at a constant rate. Calculate every 5 steps for performance reasons.
            if (step_count + iy) % 5 == 0:
                new_energy = int(g_energy[iy,ix]) + 5*(AUTOTROPH_RATE * curve(g_diet[iy,ix]) - ENERGYLOSS_RATE * curve(g_power[iy,ix]))
                if new_energy < 0:
                    g_alive[iy,ix] = False
                else:
                    g_energy[iy,ix] = new_energy
            #die from an accident
            #endsubpart_counter = perf_counter()
            #energy += subpart_counter - endsubpart_counter
            #subpart_counter = perf_counter()
            if RNG[rng_i()] > 1-DISRUPTION_RATE:
                g_alive[iy,ix] = False
                for each in NEIGHBOUR_LIST:
                    g_alive[(iy+each[1]) % GRID_SIZE,(ix+each[0]) % GRID_SIZE] = False
            #endsubpart_counter = perf_counter()
            #chance += subpart_counter - endsubpart_counter
            #endpart_counter = perf_counter()
            #beforemovement += part_counter - endpart_counter
            #part_counter = perf_counter()
            #movement
            y,x = iy,ix
            if int(g_energy[iy,ix]) > ACTIVE_TRESHOLD and bool(g_alive[iy,ix]) == True:
                #subpart_counter = perf_counter()
                #motion_counter = perf_counter()
                #rand_counter = perf_counter()
                a = bool(curve(g_motion[iy,ix]) > RNG[rng_i()])
                #endrand_counter = perf_counter()
                #rand += endrand_counter - rand_counter
                if a:
                    pick = random.choice(NEIGHBOUR_LIST)
                    g_energy[iy,ix] -= MOVEMENT_COST
                    oy = int(iy+pick[1]) % GRID_SIZE
                    ox = int(ix+pick[0]) % GRID_SIZE
                    if bool(g_alive[oy,ox]) == False:
                        #actuallymoving_counter = perf_counter()
                        g_energy[oy,ox] = g_energy[iy,ix]
                        g_diet[oy,ox] = g_diet[iy,ix]
                        g_motion[oy,ox] = g_motion[iy,ix]
                        g_power[oy,ox] = g_power[iy,ix]
                        g_alive[iy,ix] = False
                        g_alive[oy,ox] = True
                        y,x = oy,ox
                        #endactuallymoving_counter = perf_counter()
                        #actuallymoving += endactuallymoving_counter - actuallymoving_counter
            #fight and eat instead of moving if the goal has a live cell
                    else:
                        #fight_counter = perf_counter()
                        if int(g_energy[oy,ox]) < 256*(curve(g_power[iy,ix]) - FIGHTING_MODIFIER*curve(g_power[oy,ox])):
                            g_alive[oy,ox] = False
                            g_energy[iy,ix] += min(int(g_energy[oy,ox]),256*((curve(g_power[iy,ix]) - FIGHTING_MODIFIER*curve(int(g_power[oy,ox]))) * (1-curve(g_diet[iy,ix]))))
                        else:
                            g_energy[iy,ix] += min(int(g_energy[oy,ox]),256*((curve(g_power[iy,ix]) - FIGHTING_MODIFIER*curve(int(g_power[oy,ox]))) * (1-curve(g_diet[iy,ix]))))
                            g_energy[oy,ox] -= 256*(curve(g_power[iy,ix]) - FIGHTING_MODIFIER*curve(g_power[oy,ox]))
                        #endfight_counter = perf_counter()
                        #fight += endfight_counter - fight_counter
                #endmotion_counter = perf_counter()
                #motion += endmotion_counter - motion_counter
            #reproduce
                #subsubpart_counter = perf_counter()
                if g_energy[iy,ix] > REPRODUCE_TRESHOLD:
                    for i in [1,2,3]:
                        pick = random.choice(NEIGHBOUR_LIST)
                        ox = int(ix+pick[0]) % GRID_SIZE
                        oy = int(iy+pick[1]) % GRID_SIZE
                        if bool(g_alive[oy,ox]) == False or i == 3:
                            g_alive[oy,ox] = True
                            g_energy[oy,ox] = OFFSPRING_ENERGY
                            g_diet[oy,ox]   = mutate(g_diet[iy,ix])
                            g_motion[oy,ox] = mutate(g_motion[iy,ix])
                            g_power[oy,ox]  = mutate(g_power[iy,ix])             
                            g_energy[iy,ix] -= OFFSPRING_ENERGY
                            break
                #endsubsubpart_counter = perf_counter()
                #reproduce = endsubsubpart_counter - subsubpart_counter
                #endsubpart_counter = perf_counter()
                #movementloop += subpart_counter - endsubpart_counter
            #endpart_counter = perf_counter()
            #movement += part_counter - endpart_counter
            #part_counter = perf_counter()
            #death
            if int(g_energy[y,x]) > 255:
                g_energy[y,x] = 255
            elif int(g_energy[y,x]) <= 0:
                g_alive[y,x] = False
            #endpart_counter = perf_counter()
            #aftermovement += part_counter - endpart_counter
    end_time = perf_counter()
    print(f"Step Time: {end_time - start_time:0.6f}" )
    #print(f" - Before movement Time: {beforemovement:0.6f}" )
    #print(f"    - Energy: {energy:0.6f}" )
    #print(f"    - Chance: {chance:0.6f}" )
    #print(f" - Movement Time: {movement:0.6f}" )
    #print(f"    - Out of loop: {movement-movementloop:0.6f}" )
    #print(f"    - Motion     : {motion:0.6f}" )
    #print(f"        - RNG Move choice: {rand:0.6f}" )
    #print(f"        - Actually moving: {actuallymoving:0.6f}" )
    #print(f"        - Fight          : {fight:0.6f}" )
    #print(f"    - Reproduce  : {reproduce:0.6f}" )
    #print(f" - After movement Time: {aftermovement:0.6f}" )


#main loop
running = True
step_count = 0
step_countdown = 0
while running:
    time = clock.tick(FPS)
    print(time)
    draw()
    step_countdown += SPF
    while step_countdown >= 1:
        step()
        '''
        #debug predator
        if step_count > 300 and step_count < 1000:
            g_alive[(GRID_SIZE-1)//2,(GRID_SIZE-1)//2] = True
            g_energy[(GRID_SIZE-1)//2,(GRID_SIZE-1)//2] = 255
            g_motion[(GRID_SIZE-1)//2,(GRID_SIZE-1)//2] = RNG[rng_i()]*255
            g_diet[(GRID_SIZE-1)//2,(GRID_SIZE-1)//2] = RNG[rng_i()]*255
            g_power[(GRID_SIZE-1)//2,(GRID_SIZE-1)//2] = RNG[rng_i()]*255
        '''
        step_countdown -= 1
        step_count += 1
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

pg.quit()