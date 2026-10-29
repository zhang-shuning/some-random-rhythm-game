'''The scene of replays'''

from collections import deque
import struct

import pygame
import pathlib

from scenes.gameplay_scripts import *
from modules.scripts import handle_fblits
from modules.classes import Wait, WaitExtendable, PausableScene
from modules.constants import *

#The replay is in the form (time, note pos)
#0-3 for note lane 1-4, 
REPLAY_BUFFER_AMOUNT = 8
replay_header = {}
replay_buffer = deque(maxlen=8)
replay_remaining_inputs = deque()

class GamePlayScene(PausableScene):
    def __init__(self, game: GameController) -> None:
        self.gameplay_objects = GameplayScriptManager(game)
        super().__init__(game)

    def events(self, event: pygame.Event):
        if event.type == pygame.QUIT:
            #I shouldn't need any cleanup after quit, so I should be able to keep this
            #For all scenes
            self.game.running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if DEBUG:
                self.gameplay_objects.mouse_text.update_and_draw_text(f"{pygame.mouse.get_pos()}")
                print(f"mouse pos {pygame.mouse.get_pos()}")
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.running = False
            elif event.key == pygame.K_z:
                read_replay(pathlib.Path("replays/latest.replay"))
            if event.key == pygame.K_1:
                if not self.is_paused:
                    self.gameplay_objects.pause()
                else:
                    self.gameplay_objects.unpause()

    def pre_render(self):
        '''Handles the playing back of the replay'''
        update_buffer()
        while 1:
            if len(replay_buffer) == 0:
                break
            if replay_buffer[0][0] <= self.scene_ticks * replay_header["tps"] / TPS_CAP:
                if 0 <= replay_buffer[0][1] <= 3:
                    self.gameplay_objects.judge_note(replay_buffer[0][1])
                    self.gameplay_objects.held_notes[replay_buffer[0][1]] = True
                    replay_buffer.popleft()
                elif 4 <= replay_buffer[0][1] <= 7:
                    self.gameplay_objects.judge_ln_release(replay_buffer[0][1]-4)
                    self.gameplay_objects.held_notes[replay_buffer[0][1]-4] = False
                    replay_buffer.popleft()
            else:
                break

        for i in enumerate(self.gameplay_objects.held_notes):
            if self.gameplay_objects.held_notes[i[1]] is True:
                self.gameplay_objects.enable_hitlight(i[0]) 

    def render(self, screen):
        #Ensures that it still runs even if the game is paused
        if self.unpaused_ticks % FRAME_FREQUENCY == 0 or (self.is_paused and self.game.ticks % FRAME_FREQUENCY == 0):
            #Clear screen
            screen.fill((100,0,0))
            #Update score
            if self.gameplay_objects.score_updated:
                self.gameplay_objects.score_text.update_and_draw_text(f"{self.gameplay_objects.score}")
                self.gameplay_objects.score_updated = False
            if self.gameplay_objects.note_hit_or_missed:
                self.gameplay_objects.combo_text.update_and_draw_text(f"{self.gameplay_objects.combo}")
                self.acc = self.gameplay_objects.calculate_acc()
                self.gameplay_objects.acc_text.update_and_draw_text(f"{self.gameplay_objects.acc:.2f}%")
                self.gameplay_objects.note_hit_or_missed = False
            #Draw screen
            screen.fblits(handle_fblits(self.drawn_list))
            #Move notes
            if not self.is_paused:
                for note_row in self.gameplay_objects.note_list:
                    for note in note_row:
                        note.move()

            for i in self.destroy_list:
                i.destroy()
            self.destroy_list.clear()

    def scene_init(self):
        self.gameplay_objects.score_text.draw()
        self.gameplay_objects.acc_text.draw()
        self.gameplay_objects.combo_text.draw()
        self.gameplay_objects.chart.draw()
        self.gameplay_objects.judgement_line.draw()
        note_test_wrapper()
        Wait(self.game, 1, note_test_wrapper, repeats=True)
        for i in self.gameplay_objects.hit_lights:
            #some janky code
            #basically, i[0] is the light sprite, i[1] is the wait object that automatically turns off the hitlight in the list
            i.append(WaitExtendable(HITLIGHT_DISABLE_TIME, i[0].stop_draw)) # type: ignore

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
