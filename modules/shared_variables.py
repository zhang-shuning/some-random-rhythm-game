'''Contains variables that are shared between the different modules of the project'''
# pylint: disable=invalid-name

from typing import TYPE_CHECKING
import time

if TYPE_CHECKING:
    from classes import Wait

#Setup/internal buffers
surface_dict = {} #The surface dict will store drawn lists
images_dict = {} #The images dict stores all textures in the game; not dynamically loaded for now
drawn_list = [] # [[surface, pos, priority]]
fblits_list = [] # list for fblits
destroy_list = []
delta_time_list:list[Wait] = [] #List of delta time objects; this is global


class Flags():
    '''Stores all the flags'''
    running = True
    score_updated = False

class Counters():
    '''Stores all the counters'''
    ticks = 0
    score = 0
    combo = 0
    acc = 0

#Gameplay variables
note_list:list[list] = [[],[],[],[]] #List of all notes on screen
