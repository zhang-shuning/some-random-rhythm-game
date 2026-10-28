'''Contains variables that are shared between the different modules of the project'''
# pylint: disable=invalid-name

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from classes import Wait
    from pygame import Rect
    from collections.abc import Callable
    from modules.classes import Wait
    from scenes.gameplay import Note, LongNote

"""
#Setup/internal buffers
surface_dict = {} #The surface dict will store drawn lists
drawn_list = [] # [[surface, pos, priority]]
fblits_list = [] # list for fblits
destroy_list = [] # List of object to be destroyed at end of frame
rect_list:list[tuple[Rect, Callable[[]]]] = [] #List of buttons
delta_time_list:list[Wait] = [] #List of delta time objects

#Global lists
images_dict = {} #The images dict stores all textures in the game; not dynamically loaded for now
global_delta_time_list = []
scene_name_dict = {}

#Gameplay variables
note_list:list[list[LongNote|Note]] = [[],[],[],[]] #List of all notes on screen

dynamic_containers = (surface_dict,
                      drawn_list,
                      fblits_list,
                      destroy_list,
                      rect_list,
                      delta_time_list)

class Flags():
    '''Stores all the flags'''
    running = True
    score_updated = False
    note_hit_or_missed = False
    is_paused = False
    new_scene = True

class Counters():
    '''Stores all the counters'''
    ticks = 0
    @classmethod
    def reset(cls):
        '''Reset values for temporary counters'''
        cls.scene_ticks = 0
        cls.unpaused_ticks = 0
        cls.score = 0
        cls.combo = 0
        cls.acc = 0.0
        cls._300 = 0
        cls._200 = 0
        cls._100 = 0
        cls._50 = 0
        cls.miss = 0

Counters.reset()

class StringFlags():
    cur_scene:str = ''
"""