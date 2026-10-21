'''The scene of replays'''

from collections import deque
import struct

import pygame
import pathlib

from scenes.gameplay_scripts import *
from modules.scripts import handle_fblits
from modules.classes import Wait, Text, Sprite, WaitExtendable, DrawbleRect, Scene, Button
from modules.constants import *
from modules.shared_variables import *

#The replay is in the form (time, note pos)
#0-3 for note lane 1-4, 
REPLAY_BUFFER_AMOUNT = 8
replay_header = {}
replay_buffer = deque(maxlen=8)
replay_remaining_inputs = deque()

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
        elif event.key == pygame.K_z:
            read_replay(pathlib.Path("replays/latest.replay"))
        if event.key == pygame.K_1:
            if not Flags.is_paused:
                pause()
            else:
                unpause()

def pre_render():
    '''Handles the playing back of the replay'''
    update_buffer()
    while 1:
        if len(replay_buffer) == 0:
            break
        if replay_buffer[0][0] <= Counters.scene_ticks * replay_header["tps"] / TPS_CAP:
            print(f"time {replay_buffer[0][0]} buffer {replay_buffer[0][1]}")
            if 0 <= replay_buffer[0][1] <= 3:
                judge_note(replay_buffer[0][1])
                held_notes[replay_buffer[0][1]] = True
                replay_buffer.popleft()
            elif 4 <= replay_buffer[0][1] <= 7:
                judge_ln_release(replay_buffer[0][1]-4)
                held_notes[replay_buffer[0][1]-4] = False
                replay_buffer.popleft()
        else:
            break

    for i in enumerate(held_notes):
        if held_notes[i[1]] is True:
            enable_hitlight(i[0]) 

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
    read_replay(pathlib.Path("replays/latest.replay"))

def scene_cleanup():
    for i in note_list:
        i.clear()
    replay_header.clear()
    replay_buffer.clear()
    replay_remaining_inputs.clear()
    for i in range(4):
        held_notes[i] = False

def make_scene():
    '''
    Function that makes the scene
    Thinking back, it might've been better to just put this in the class...
    '''
    Scene("replay", events, pre_render=pre_render, render=render, scene_init_function=scene_init, scene_cleanup=scene_cleanup)

def read_replay(replay_file:pathlib.Path):
    '''Reads the replay and returns a tuple of data'''
    with open(replay_file, "rb") as f:
        f.seek(6)
        header = f.read(9)
        header_info = struct.unpack(">bii", header)
        replay_header["version"] = header_info[0]
        replay_header["fps"] = header_info[1]
        replay_header['tps'] = header_info[2]
        if header_info[0] == 1:
            data = f.read() #It's better to read in chunks, but effort...
            if len(data) % 5 != 0:
                print("Something went wong with the replay")
                return
            for i in range(len(data)//5):
                cur_input = struct.unpack(">ib", data[i*5:i*5+5])
                replay_remaining_inputs.append((cur_input[0], cur_input[1]))

def update_buffer():
    for _ in range(REPLAY_BUFFER_AMOUNT-len(replay_buffer)):
        if len(replay_remaining_inputs) != 0:
            replay_buffer.append(replay_remaining_inputs[0])
            replay_remaining_inputs.popleft()
