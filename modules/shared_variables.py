'''Contains variables that are shared between the different modules of the project'''

import pygame

surface_dict = {} #The surface dict will store drawn lists with surface pos and priority
drawn_list = [] # [[surface, pos, priority]]
delta_time_list = [] #List of delta time objects
cur_time = 0