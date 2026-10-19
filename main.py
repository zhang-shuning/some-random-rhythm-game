'''Main file for the game'''
# pylint: disable=no-member
from random import randint
import time
import pygame
import sys

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

current_scene = scenes.gameplay.scene
scenes.gameplay.draw_assets()

#Just spawns some notes every 3 seconds
def note_test_wrapper():
    random_1 = randint(1,4)
    scenes.gameplay.Note(random_1).draw()
    if randint(0,3) == 0:
        while 1:
            random_2 = randint(1,4)
            if random_1 != random_2:
                scenes.gameplay.LongNote(random_2, 10)
                break

note_test_wrapper()
Wait(1, note_test_wrapper, repeats=True, use_game_tick=True)

#Text declaration
fps_text = Text("0", (HORIZONTAL_SIZE, 0), 100, origin=(1,0))

#Button function declaration
def pause():
    Flags.is_paused = True
    unpause_button.draw()
    restart_button.draw()
    exit_button.draw()

def unpause():
    Flags.is_paused = False
    unpause_button.stop_draw()
    restart_button.stop_draw()
    exit_button.stop_draw()

def stop_game():
    Flags.running=False

unpause_button = Button("Return to game", (960, 300), 100, origin=(.5,.5), rect_color=(128,128,128), rect_size=(200,100), on_press=unpause)
restart_button = Button("Return to game", (960, 500), 100, origin=(.5,.5), rect_color=(128,128,128), rect_size=(200,100), on_press=unpause)
exit_button = Button("Exit", (960, 700), 100, origin=(.5,.5), rect_color=(128,128,128), rect_size=(200,100), on_press=stop_game)

def fps_wrapper(): fps_text.update_and_draw_text(f"{clock.get_fps():.5f}")
fps_text.draw()
fps_update = Wait(.1, fps_wrapper, repeats=True)

#This system checks if a note is out sync with the actual time
expected_time = time.time()
cur_time = time.time()
ticks_to_increment = 1

#Main loop
while Flags.running:
    #Get events
    for event in pygame.event.get():
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
