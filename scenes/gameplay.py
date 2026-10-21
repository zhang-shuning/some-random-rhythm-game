import pathlib
import struct

import pygame

from scenes.gameplay_scripts import *
from modules.scripts import handle_fblits
from modules.classes import Wait, WaitExtendable, Scene
from modules.shared_variables import *

#Input array
input_array = []

def events(event: pygame.Event):
    if event.type == pygame.QUIT:
        #I shouldn't need any cleanup after quit, so I should be able to keep this
        #For all scenes
        Flags.running = False
        if DEBUG:
            mouse_text.update_and_draw_text(f"{pygame.mouse.get_pos()}")
            print(f"mouse pos {pygame.mouse.get_pos()}")
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            Flags.running = False
        if event.key == pygame.K_d:
            judge_note(0)
            keypress.play()
            held_notes[0] = True
            input_array.append((Counters.ticks, 0))
        elif event.key == pygame.K_f:
            judge_note(1)
            keypress.play()
            held_notes[1] = True
            input_array.append((Counters.ticks, 1))
        elif event.key == pygame.K_j:
            judge_note(2)
            keypress.play()
            held_notes[2] = True
            input_array.append((Counters.ticks, 2))
        elif event.key == pygame.K_k:
            judge_note(3)
            keypress.play()
            input_array.append((Counters.ticks, 3))
            held_notes[3] = True
        elif event.key == pygame.K_z:
            save_replay()
    if event.type == pygame.KEYUP:
        if event.key == pygame.K_d:
            judge_ln_release(0)
            held_notes[0] = False
            input_array.append((Counters.ticks, 4))
        elif event.key == pygame.K_f:
            judge_ln_release(1)
            held_notes[1] = False
            input_array.append((Counters.ticks, 5))
        elif event.key == pygame.K_j:
            judge_ln_release(2)
            held_notes[2] = False
            input_array.append((Counters.ticks, 6))
        elif event.key == pygame.K_k:
            judge_ln_release(3)
            held_notes[3] = False
            input_array.append((Counters.ticks, 7))
        if event.key == pygame.K_1:
            if not Flags.is_paused:
                pause()
            else:
                unpause()

def held_keys(keys):
    #Only check if the frame is being drawn for hitlights because hitlights are rendered
    if Counters.game_ticks % FRAME_FREQUENCY == 0:
        if not Flags.is_paused:
            if keys[pygame.K_d]:
                enable_hitlight(0)
            if keys[pygame.K_f]:
                enable_hitlight(1)
            if keys[pygame.K_j]:
                enable_hitlight(2)
            if keys[pygame.K_k]:
                enable_hitlight(3)

def render(screen):
    #Rendering
    if Counters.game_ticks % FRAME_FREQUENCY == 0 or (Flags.is_paused and Counters.ticks % FRAME_FREQUENCY == 0):
        #Clear screen
        screen.fill((100,0,0))
        #Update score
        if Flags.score_updated:
            score_text.update_and_draw_text(f"{Counters.score}")
            Flags.score_updated = False
        if Flags.note_hit_or_missed:
            combo_text.update_and_draw_text(f"{Counters.combo}")
            calculate_acc()
            acc_text.update_and_draw_text(f"{Counters.acc:.2f}%")
            Flags.note_hit_or_missed = False
        #Draw screen
        handle_fblits()
        screen.fblits(fblits_list)
        #Move notes
        if not Flags.is_paused:
            for note_row in note_list:
                for note in note_row:
                    note.move()

        for i in destroy_list:
            i.destroy()
        destroy_list.clear()

        pygame.display.flip()

def scene_cleanup():
    Counters.reset()
    for i in note_list:
        i.clear()

def scene_init():
    score_text.draw()
    acc_text.draw()
    combo_text.draw()
    chart.draw()
    judgement_line.draw()
    note_test_wrapper()
    Wait(1, note_test_wrapper, repeats=True, use_game_tick=True)
    for i in hit_lights:
        i.append(WaitExtendable(HITLIGHT_DISABLE_TIME, i[0].stop_draw))

def make_scene():
    Scene("gameplay", events, held_keys, render, scene_init_function=scene_init, scene_cleanup=scene_cleanup)

def stop_assets():
    score_text.stop_draw()
    acc_text.stop_draw()
    combo_text.stop_draw()
    chart.stop_draw()
    judgement_line.stop_draw()
    note_list.clear()

def make_replay_bytearray() -> bytearray:
    #Version (8 bits)
    #Framerate
    #Tick rate
    #32 bits gameticks, 4 bits time
    byte_list = bytearray(b"RPLY\032\n")
    byte_list.append(1)
    byte_list += struct.pack(">ii", FPS_CAP, TPS_CAP)
    for i in input_array:
        if i[0] > 2**32-1:
            raise ValueError("Time is too big.")
        byte_list += struct.pack(">ib", i[0], i[1])
    print(byte_list)
    return byte_list

def save_replay():
    pathlib.Path("replays").mkdir(exist_ok=True)
    with open(pathlib.Path("replays/latest.replay"), 'wb') as f:
        f.write(make_replay_bytearray())
