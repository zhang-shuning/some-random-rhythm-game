'''Main file for the game'''
# pylint: disable=no-member
from random import randint
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
mouse_text = Text("", (HORIZONTAL_SIZE-500,0), 100)
fps_text = Text("0", (HORIZONTAL_SIZE, 0), 100, origin=(1,0))
score_text = Text("0", (HORIZONTAL_SIZE, 25), 100, font_size=40, origin=(1,0))
acc_text = Text("100.00%", (HORIZONTAL_SIZE, 60), 100, font_size=40, origin=(1,0))
combo_text = Text("0", (0, VERTICAL_SIZE), 100, font_size=100, origin=(0,1))

#Button function declaration
def pause():
    Flags.is_paused = True
    Flags.current_frame_drawn = False
    unpause_button.draw()
    restart_button.draw()
    exit_button.draw()

def unpause():
    Flags.is_paused = False
    Flags.current_frame_drawn = True
    unpause_button.stop_draw()
    restart_button.stop_draw()
    exit_button.stop_draw()

def stop_game():
    Flags.running=False

unpause_button = Button("Return to game", (960, 300), 100, origin=(.5,.5), rect_color=(128,128,128), rect_size=(200,100), on_press=unpause)
restart_button = Button("Return to game", (960, 500), 100, origin=(.5,.5), rect_color=(128,128,128), rect_size=(200,100), on_press=unpause)
exit_button = Button("Exit", (960, 700), 100, origin=(.5,.5), rect_color=(128,128,128), rect_size=(200,100), on_press=stop_game)

score_text.draw()
acc_text.draw()
combo_text.draw()

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
        if event.type == pygame.QUIT:
            Flags.running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            #Button check
            for i in rect_list:
                if i[0].collidepoint(event.pos):
                    i[1]()
            if DEBUG:
                mouse_text.update_and_draw_text(f"{pygame.mouse.get_pos()}")
                print(f"mouse pos {pygame.mouse.get_pos()}")
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                Flags.running = False
            if Flags.current_frame_drawn:
                if event.key == pygame.K_d:
                    scenes.gameplay.judge_note(0)
                    scenes.gameplay.keypress.play()
                    held_notes[0] = True
                elif event.key == pygame.K_f:
                    scenes.gameplay.judge_note(1)
                    scenes.gameplay.keypress.play()
                    held_notes[1] = True
                elif event.key == pygame.K_j:
                    scenes.gameplay.judge_note(2)
                    scenes.gameplay.keypress.play()
                    held_notes[2] = True
                elif event.key == pygame.K_k:
                    scenes.gameplay.judge_note(3)
                    scenes.gameplay.keypress.play()
                    held_notes[3] = True
        if event.type == pygame.KEYUP:
            if Flags.current_frame_drawn:
                if event.key == pygame.K_d:
                    scenes.gameplay.judge_ln_release(0)
                    held_notes[0] = False
                elif event.key == pygame.K_f:
                    scenes.gameplay.judge_ln_release(1)
                    held_notes[1] = False
                elif event.key == pygame.K_j:
                    scenes.gameplay.judge_ln_release(2)
                    held_notes[2] = False
                elif event.key == pygame.K_k:
                    scenes.gameplay.judge_ln_release(3)
                    held_notes[3] = False
            if event.key == pygame.K_1:
                if not Flags.is_paused:
                    pause()
                else:
                    unpause()


    #Held keys
    keys = pygame.key.get_pressed()
    #Only check if the frame is being drawn for hitlights because hitlights are rendered
    if Counters.game_ticks % FRAME_FREQUENCY == 0:
        if Flags.current_frame_drawn:
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
    if Counters.game_ticks % FRAME_FREQUENCY == 0:
        #Clear screen
        screen.fill((100,0,0))
        #Update score
        if Flags.score_updated:
            score_text.update_and_draw_text(f"{Counters.score}")
            Flags.score_updated = False
        if Flags.note_hit_or_missed:
            combo_text.update_and_draw_text(f"{Counters.combo}")
            scenes.gameplay.calculate_acc()
            acc_text.update_and_draw_text(f"{Counters.acc:.2f}%")
            Flags.note_hit_or_missed = False
        #Draw screen
        handle_fblits()
        screen.fblits(fblits_list)
        #Draw notes
        if Flags.current_frame_drawn:
            for note_row in note_list:
                for note in note_row:
                    note.move()

        for i in destroy_list:
            i.destroy()
        destroy_list.clear()

        pygame.display.flip()

    #If time is too off the expected time, go multiple ticks instead
    expected_time += S_PER_TICK
    cur_time = time.time()

    #Check frame drops
    if cur_time > expected_time:
        #Calculate how many ticks the time has gone up by
        ticks_to_increment = int((cur_time-expected_time) / S_PER_TICK)
        expected_time += ticks_to_increment*S_PER_TICK

    #Next tick
    if Flags.current_frame_drawn:
        Counters.game_ticks+=1
    Counters.ticks+=1
    clock.tick(TPS_CAP)
