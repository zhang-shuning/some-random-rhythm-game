'''Main file for the game'''
# pylint: disable=no-member
from random import randint
import pygame

from modules.classes import Text, Wait, Sprite, WaitExtendable
from modules.constants import *
from modules.shared_variables import *
from modules.scripts import load_images, handle_fblits

#Pygame variable initialization
screen:pygame.Surface = pygame.display.set_mode((HORIZONTAL_SIZE, VERTICAL_SIZE),pygame.FULLSCREEN | pygame.SCALED)
clock:pygame.time.Clock = pygame.time.Clock()
pygame.init()
load_images()

import scenes.gameplay

scenes.gameplay.draw_assets()

#Just spawns some notes every 3 seconds
def note_test_wrapper():
    random_1 = randint(1,4)
    scenes.gameplay.Note(random_1).draw()
    if randint(0,3) == 0:
        while 1:
            random_2 = randint(1,4)
            if random_1 != random_2:
                scenes.gameplay.Note(random_2).draw()
                break

note_test_wrapper()
Wait(.2, note_test_wrapper, repeats=True)

#Text declaration
mouse_text = Text("", (HORIZONTAL_SIZE-200,0), 100)
fps_text = Text("0", (0, 0), 100)
score_text = Text("score: 0", (0, 25), 100)
score_text.draw()

def fps_wrapper(): fps_text.update_and_draw_text(str(clock.get_fps()))
fps_text.draw()
fps_update = Wait(.1, fps_wrapper, repeats=True)

#Main loop
while Flags.running:
    #Get events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Flags.running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if DEBUG:
                mouse_text.update_and_draw_text(f"{pygame.mouse.get_pos()}")
                print(f"mouse pos {pygame.mouse.get_pos()}")
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                Flags.running = False
            elif event.key == pygame.K_d:
                scenes.gameplay.judge_note(0)
                scenes.gameplay.keypress.play()
            elif event.key == pygame.K_f:
                scenes.gameplay.judge_note(1)
                scenes.gameplay.keypress.play()
            elif event.key == pygame.K_j:
                scenes.gameplay.judge_note(2)
                scenes.gameplay.keypress.play()
            elif event.key == pygame.K_k:
                scenes.gameplay.judge_note(3)
                scenes.gameplay.keypress.play()

    #Held keys
    keys = pygame.key.get_pressed()
    #Only check if the frame is being drawn for hitlights because hitlights are rendered
    if Counters.ticks % FRAME_FREQUENCY == 0:
        if keys[pygame.K_d]:
            scenes.gameplay.enable_hitlight(0)
        if keys[pygame.K_f]:
            scenes.gameplay.enable_hitlight(1)
        if keys[pygame.K_j]:
            scenes.gameplay.enable_hitlight(2)
        if keys[pygame.K_k]:
            scenes.gameplay.enable_hitlight(3)

    #Get delta time events
    for i in delta_time_list:
        if i.time_passed():
            i.run()

    #Rendering
    if Counters.ticks % FRAME_FREQUENCY == 0:
        #Clear screen
        screen.fill((0,0,0))
        #Update score
        if Flags.score_updated:
            score_text.update_and_draw_text(f"{Counters.score}")
        #Draw screen
        handle_fblits()
        screen.fblits(fblits_list)
        #Draw notes
        for note_row in note_list:
            for note in note_row:
                note.move()

        for i in destroy_list:
            i.destroy()
        destroy_list.clear()

        pygame.display.flip()

    #Next tick
    Counters.ticks+=1
    clock.tick(TPS_CAP)
