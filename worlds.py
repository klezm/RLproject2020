import textwrap
import re

import numpy as np


# ##############################################################################
# ############################ Grid World Templates ############################
# ##############################################################################

# Templates may contain spaces, S(tart), G(oal) and # for walls
# separate each template by a line with --- this line also may contain comments a the end

grid_worlds = """\
----------------- 1 |  empty world (just resets everything)

----------------- 2 | simple dummy world with one starting point and one goal

  G ##
 ####   S

   #
----------------- 3 | for 6x6 gridworld
      
 G    
      
##### 
      
 S    
----------------- 4 | for 6x6 gridworld
 G    
      
##### 
      
##    
----------------- 5 | 6x6
#     
 #  G 
 S#   
   #  
    # 
      
----------------- 6 | 6x6
     #
 G   #
#### #
     #
 #####
      
----------------- 7 | 6x6
      
 G    
   #  
  #   
      
----------------- 8 | 
         
 G       
   #     
  #      
         
      #  
     #   
         
        S
-------------------- 9 | 6x6
      
  #   
S   #G
  #   
      
      
----------------- 10 |  9x9
G        
         
  G      
         
######   
         
         
###      
         
----------------- 11 |
S       S
         
         
         
    G    
         
         
         
S       S
----------------- 12 |
         
  G      
         
#######  
         
         
###      
         
-------------------- 13 |

 S




       G
-------------------- 14 | --grid-shape 9 --steps 1000000 --refresh-rate 1 --show-rate 100 --off-policy --grid-world-template 14
         
         
      G  
   #     
  G#     
   #     
      G  
         
         
-------------------- 15 |
 
 G G G G
         
 G G G G
         
         
   ###   
    G    
         
         
-------------------- 16 |
"""

# ##############################################################################
# ##############################################################################
# ##############################################################################

# convert the single string worlds into a list of worlds

grid_worlds = re.split(r"\s*---+.*?\n", grid_worlds)

# remove duplicates
gws = []
for g in grid_worlds:
    if g not in gws:
        gws.append(g)
grid_worlds = gws
del gws
# print(grid_worlds, *grid_worlds, sep = "\n" + "."*50 + "\n")


def make_grid_world(world: str):
    # world = textwrap.dedent(world)

    # adjust lengths => make a rectangular matrix
    world = world.split("\n")
    max_len = max(map(len, world))
    world = [[world[l][c] if c < len(world[l]) else " " for c in range(max_len)] for l in range(len(world))]

    # flip & rotate
    world = np.rot90(np.fliplr(world))

    return world


grid_worlds = [make_grid_world(x) for x in grid_worlds]
