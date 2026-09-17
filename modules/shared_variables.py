'''Contains variables that are shared between the different modules of the project'''

from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from classes import *

surface_dict = {} #The surface dict will store drawn lists
drawn_list = [] # [[surface, pos, priority]]
delta_time_list:list[Wait] = [] #List of delta time objects; this is global
cur_time = 0