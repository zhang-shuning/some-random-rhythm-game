import pathlib
import struct

import pygame

from main import GameController
from scenes.gameplay_scripts import *
from modules.scripts import handle_fblits
from modules.classes import Wait, WaitExtendable, PausableScene

if TYPE_CHECKING:
    from typing import TYPE_CHECKING

class GameplayScene(PausableScene):
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
            if event.key == pygame.K_d:
                self.gameplay_objects.judge_note(0)
                self.gameplay_objects.keypress.play()
                self.gameplay_objects.held_notes[0] = True
                input_array.append((self.unpaused_ticks, 0))
            elif event.key == pygame.K_f:
                self.gameplay_objects.judge_note(1)
                self.gameplay_objects.keypress.play()
                self.gameplay_objects.held_notes[1] = True
                input_array.append((self.unpaused_ticks, 1))
            elif event.key == pygame.K_j:
                self.gameplay_objects.judge_note(2)
                self.gameplay_objects.keypress.play()
                self.gameplay_objects.held_notes[2] = True
                input_array.append((self.unpaused_ticks, 2))
            elif event.key == pygame.K_k:
                self.gameplay_objects.judge_note(3)
                self.gameplay_objects.keypress.play()
                input_array.append((self.unpaused_ticks, 3))
                self.gameplay_objects.held_notes[3] = True
            elif event.key == pygame.K_z:
                save_replay()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                self.gameplay_objects.judge_ln_release(0)
                self.gameplay_objects.held_notes[0] = False
                input_array.append((self.unpaused_ticks, 4))
            elif event.key == pygame.K_f:
                self.gameplay_objects.judge_ln_release(1)
                self.gameplay_objects.held_notes[1] = False
                input_array.append((self.unpaused_ticks, 5))
            elif event.key == pygame.K_j:
                self.gameplay_objects.judge_ln_release(2)
                self.gameplay_objects.held_notes[2] = False
                input_array.append((self.unpaused_ticks, 6))
            elif event.key == pygame.K_k:
                self.gameplay_objects.judge_ln_release(3)
                self.gameplay_objects.held_notes[3] = False
                input_array.append((self.unpaused_ticks, 7))
            if event.key == pygame.K_1:
                if not self.is_paused:
                    self.gameplay_objects.pause()
                else:
                    self.gameplay_objects.unpause()

    def held_keys(self, keys):
        #Only check if the frame is being drawn for hitlights because hitlights are rendered
        if self.unpaused_ticks % FRAME_FREQUENCY == 0:
            if not self.is_paused:
                if keys[pygame.K_d]:
                    self.gameplay_objects.enable_hitlight(0)
                if keys[pygame.K_f]:
                    self.gameplay_objects.enable_hitlight(1)
                if keys[pygame.K_j]:
                    self.gameplay_objects.enable_hitlight(2)
                if keys[pygame.K_k]:
                    self.gameplay_objects.enable_hitlight(3)

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


#Input array
input_array = []

def make_replay_bytearray() -> bytearray:
    '''Returns a bytearray containing the binary data for the replay'''
    #Header
    #ID
    byte_list = bytearray(b"RPLY\032\n")
    #Version number
    byte_list.append(1)

    if FPS_CAP > 2**32-1:
        raise ValueError("FPS cap is too big")
    if TPS_CAP > 2**32-1:
        raise ValueError("TPS cap is too big")
    #FPS cap and TPS cap
    byte_list += struct.pack(">ii", FPS_CAP, TPS_CAP)

    #Data
    for i in input_array:
        #The data is 4 bytes time, 1 byte the key
        if i[0] > 2**32-1:
            raise ValueError("Time is too big.")
        byte_list += struct.pack(">ib", i[0], i[1])
    return byte_list

def save_replay():
    pathlib.Path("replays").mkdir(exist_ok=True)
    with open(pathlib.Path("replays/latest.replay"), 'wb') as f:
        f.write(make_replay_bytearray())
