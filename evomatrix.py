import Tkinter as grid
import random
import sched, time

g_cols, g_rows = 50,50
g_energy = [[0 for x in range(g_cols)] for y in range(g_rows)] 

root = grid.Tk()

def draw_grid():
    w = c.winfo_width()
    h = c.winfo_height()
    cs = min(w/g_cols,h/g_rows)
    
    c.delete('cell')

    for x in range(0, g_cols):
        for y in range(0, g_rows):
            cellcolor = '#' + str(int(g_energy[x][y])) + str(int(g_energy[x][y])) + str(int(g_energy[x][y]))
            c.create_rectangle(x*cs,y*cs,x*cs+cs,y*cs+cs,fill=cellcolor, tag='cell')


def step_grid():
    for x in range(0, g_cols):
        for y in range(0, g_rows):
            g_energy[x][y] = random.randint(0,10)
    root.after(100, step_grid)
    root.after(50, draw_grid)
root.after(0, step_grid)


c = grid.Canvas(root, height=1000, width=1000, bg='#000')
c.pack(fill=grid.BOTH, expand=True)

c.bind('<Configure>', draw_grid)

root.mainloop()