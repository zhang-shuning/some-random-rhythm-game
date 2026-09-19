'''Contains variables that are shared between the different modules of the project'''

from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from classes import *

#Setup/internal buffers
surface_dict = {} #The surface dict will store drawn lists
images_dict = {} #The images dict stores all textures in the game; not dynamically loaded for now
drawn_list = [] # [[surface, pos, priority]]
fblits_list = [] # list for fblits
delta_time_list:list[Wait] = [] #List of delta time objects; this is global
cur_time = 0 #Current unix time

#Gameplay variables
running = True
note_list = [] #List of all notes on screen