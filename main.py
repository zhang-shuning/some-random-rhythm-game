'''Main file for the game'''
# pylint: disable=no-member
import time
import pygame

from modules.classes import Text, Wait, Button
from modules.constants import *
from modules.shared_variables import *
from modules.scripts import load_images, handle_fblits

#Pygame variable initialization
screen:pygame.Surface = pygame.display.set_mode((HORIZONTAL_SIZE, VERTICAL_SIZE),pygame.FULLSCREEN | pygame.SCALED)
clock:pygame.time.Clock = pygame.time.Clock()
pygame.init()
load_images()

import scenes.gameplay
import scenes.level_selector
import scenes.main_menu

current_scene = scenes.main_menu.scene

#Text declaration
fps_text = Text("0", (HORIZONTAL_SIZE, 0), 100, origin=(1,0))

def fps_wrapper(): fps_text.update_and_draw_text(f"{clock.get_fps():.5f}")
fps_text.draw()
fps_update = Wait(.1, fps_wrapper, repeats=True)

#This system checks if a note is out sync with the actual time
expected_time = time.time()
cur_time = time.time()
ticks_to_increment = 1

#Main loop
while Flags.running:
    if Flags.new_scene:
        current_scene.init_scene()
    #Get events
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            #Button check
            for i in rect_list:
                if i[0].collidepoint(event.pos):
                    i[1]()

        current_scene.handle_event(event)

    #Held keys
    keys = pygame.key.get_pressed()
    current_scene.handle_held_keys(keys)

    #Get delta time events
    for i in delta_time_list:
        if i.time_passed():
            i.run()

    #Render
    current_scene.render(screen)

    #If time is too off the expected time, go multiple ticks instead
    expected_time += S_PER_TICK
    cur_time = time.time()

    #Check frame drops
    if cur_time > expected_time:
        #Calculate how many ticks the time has gone up by
        ticks_to_increment = int((cur_time-expected_time) / S_PER_TICK)
        expected_time += ticks_to_increment*S_PER_TICK

    #Next tick
    if not Flags.is_paused:
        Counters.game_ticks+=1
    Counters.ticks+=1

    Flags.new_scene = False

    clock.tick(TPS_CAP)
