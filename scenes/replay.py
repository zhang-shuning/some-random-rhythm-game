'''The scene of replays'''

import struct
import enum

import pygame
import pathlib

from scenes.gameplay_scripts import *
from modules.scripts import handle_fblits
from modules.classes import Wait, Text, Sprite, WaitExtendable, DrawbleRect, Scene, Button
from modules.constants import *
from modules.shared_variables import *

REPLAY_BUFFER_AMOUNT = 8
replay_header = {}
replay_buffer = []
replay_remaining_inputs = []

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
        elif event.key == pygame.K_f:
            judge_note(1)
            keypress.play()
            held_notes[1] = True
        elif event.key == pygame.K_j:
            judge_note(2)
            keypress.play()
            held_notes[2] = True
        elif event.key == pygame.K_k:
            judge_note(3)
            keypress.play()
            held_notes[3] = True
        elif event.key == pygame.K_z:
            read_replay(pathlib.Path("replays/latest.replay"))
    if event.type == pygame.KEYUP:
        if event.key == pygame.K_d:
            judge_ln_release(0)
            held_notes[0] = False
        elif event.key == pygame.K_f:
            judge_ln_release(1)
            held_notes[1] = False
        elif event.key == pygame.K_j:
            judge_ln_release(2)
            held_notes[2] = False
        elif event.key == pygame.K_k:
            judge_ln_release(3)
            held_notes[3] = False
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

def scene_cleanup():
    Counters.reset()
    for i in note_list:
        i.clear()
    replay_header.clear()
    replay_header.clear()
    replay_remaining_inputs.clear()

def make_scene():
    '''
    Function that makes the scene
    Thinking back, it might've been better to just put this in the class...
    '''
    Scene("replay", events, held_keys, render, scene_init_function=scene_init, scene_cleanup=scene_cleanup)

def read_replay(replay_file:pathlib.Path):
    '''Reads the replay and returns a tuple of data'''
    with open(replay_file, "rb") as f:
        f.seek(6)
        header = f.read(9)
        header_info = struct.unpack(">bii", header)
        replay_header["version"] = header_info[0]
        replay_header["fps"] = header_info[1]
        replay_header['inputs'] = header_info[2]
        if header_info[0] == 1:
            print("version 1")
            data = f.read() #It's better to read in chunks, but effort...
            if len(data) % 5 != 0:
                print("Something went wong with the replay")
                return ()
            for i in range(len(data)//5):
                print(data[i*5:i*5+5])
                cur_input = struct.unpack(">ib", data[i*5:i*5+5])
                replay_remaining_inputs.append((cur_input[0], cur_input[1]))

def update_buffer():
    for _ in range(REPLAY_BUFFER_AMOUNT-len(replay_buffer)):
        if len(replay_remaining_inputs) != 0:
            replay_buffer.append(replay_remaining_inputs[0])
