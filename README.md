# evomatrix
Personal project which simulates speciation through natural selection using python.

`Python3 evomatrix.py` to run.
Resize window to see 3D scatterplot of genetic variation.
Presets (global constants) can be changed in the code.
TPS (ticks/steps per second) and FPS (frames/renders per second) can be changed for better visual performance or simulation speed.
An article about this can be found here: https://www.dries.page/life

## How it works:
 - A grid is created. In the beginning Every cell (the little squares) is empty except for the central cell.
 - Non-empty cells are alive, they have energy between 0 and 1 and 3 genes (red: power, green: photosynthesis, blue: speed).
 - They will lose energy every tick, and lose extra energy for being more powerful or fast.
 - The green gene determines their method of feeding. The greener cells are, the better they can feed autotrophically (gain energy automatically, take energy from outside the system, like sunlight). 
 - When reaching a certain energy treshold (0.9 by default), the cell will split and the offspring will inherit the same genes with slight mutation (along a long-tailed gauss curve).
 - The less they feed autotrophically, the better they are at consuming energy from other cells after colliding with them (heterotrophy). The cell which hits the other cell removes energy from it proportional to the attackers power (red gene), and turns some of that into energy for himself proportional to how heterotrophic it is. Then the defender, if still alive, can do the same with the attacker.
 
 With these simple mechanisms it is possible to demonstrate many ecological and evolutionary concepts including:
 
  - Genetic drift
  - Adaptation
  - Speciation through natural selection
  - Fast‐Slow Dynamical Systems
  - Lotka-Volterra cycles
  - Ecological disturbance
  - Genetic trade-offs
  - Extinction
  - Equilibrium
