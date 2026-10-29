'''Scripts used in both actual gameplay and the replay.'''
from random import randint
from collections import deque
from abc import ABC, abstractmethod
from typing import override, TYPE_CHECKING

import pygame

from modules.classes import Wait, Text, Sprite, WaitExtendable, DrawbleRect, PausableScene, Button
from modules.constants import *

if TYPE_CHECKING:
    from main import GameController

class GameplayScriptManager():
    def __init__(self, game:GameController) -> None:
        self.scene = game.cur_scene
        if not isinstance(self.scene, PausableScene):
            raise ValueError("Something went wrong, GameplayScriptManager attempted to be initialized with a non-pausable scene.")
        #init
        self.game = game
        self.jth = JudgementTextHandler(self)

        #sfx
        self.hit = pygame.Sound("assets/sfx/hit.wav")
        self.keypress = pygame.Sound("assets/sfx/keypress.wav")
        self.miss = pygame.Sound("assets/sfx/miss.wav")

        self.hit.set_volume(.1)
        self.keypress.set_volume(.2)
        self.miss.set_volume(.6)

        self.note_list = []

        #Score/hits
        self.score_updated = False
        self.note_hit_or_missed = True
        self.score = 0
        self.combo = 0
        self.acc = 0.0
        self.hits_300 = 0
        self.hits_200 = 0
        self.hits_100 = 0
        self.hits_50 = 0
        self.miss_0 = 0

        #Text
        self.mouse_text = Text(game, "", (HORIZONTAL_SIZE-500,0), 100)
        self.score_text = Text(game, "0", (HORIZONTAL_SIZE, 25), 100, font_size=40, origin=(1,0))
        self.acc_text = Text(game, "100.00%", (HORIZONTAL_SIZE, 60), 100, font_size=40, origin=(1,0))
        self.combo_text = Text(game, "0", (0, VERTICAL_SIZE), 100, font_size=100, origin=(0,1))
        self.excellent_text = Text(game, "Excellent", JUDEMENT_TEXT_POS, 10, font_size=120, text_color=(0, 150, 255), origin=(.5,.5))
        self.good_text = Text(game, "Good", JUDEMENT_TEXT_POS, 10, font_size=150, text_color=(34, 139, 34), origin=(.5,.5))
        self.ok_text = Text(game, "OK", JUDEMENT_TEXT_POS, 10, font_size=150, text_color=(175, 225, 175), origin=(.5,.5))
        self.bad_text = Text(game, "Bad", JUDEMENT_TEXT_POS, 10, font_size=150, text_color=(211, 211, 211), origin=(.5,.5))
        self.miss_text = Text(game, "Miss!", JUDEMENT_TEXT_POS, 10, font_size=150, text_color=(255, 0, 0), origin=(.5,.5))

        #Sprites
        self.chart = Sprite(game, -10, (HORIZONTAL_SIZE/2-400, 0), "chart")
        self.judgement_line = Sprite(game, -9, (HORIZONTAL_SIZE/2-400, VERTICAL_SIZE-JUDGEMENT_LINE_HEIGHT), "judgement_line")
        self.hit_lights:list[list[Sprite|WaitExtendable]] = [[Sprite(game, -8.5, (560+200*x, VERTICAL_SIZE-250), "hit_light")] for x in range(4)]

        self.held_notes = [False, False, False, False]
        #Buttons
        self.unpause_button = Button(game, "Return to game", (960, 300), 100, origin=(.5,.5), rect_color=(128,128,128), rect_size=(200,100), on_press=self.unpause)
        self.restart_button = Button(game, "Return to game", (960, 500), 100, origin=(.5,.5), rect_color=(128,128,128), rect_size=(200,100), on_press=self.unpause)
        self.exit_button = Button(game, "Exit", (960, 700), 100, origin=(.5,.5), rect_color=(128,128,128), rect_size=(200,100), on_press=self.stop_game)

    #Button function declaration
    def pause(self):
        self.is_paused = True
        self.unpause_button.draw()
        self.restart_button.draw()
        self.exit_button.draw()

    def unpause(self):
        self.is_paused = False
        self.unpause_button.stop_draw()
        self.restart_button.stop_draw()
        self.exit_button.stop_draw()

    def stop_game(self):
        self.unpause()
        self.game.new_scene = True
        self.game.next_scene_str = "level_selector"

    def enable_hitlight(self, n):
        '''Enables the hitlight'''
        self.hit_lights[n][1].set_time()
        if not self.hit_lights[n][0].is_drawn:
            self.hit_lights[n][0].draw()

    def judge_note(self, lane:int):
        if len(self.note_list[lane]) == 0:
            return

        note = self.note_list[lane][0]
        if isinstance(note, AbstractNote):
            cur_score = note.judge()
            #Handle point scoring
            if cur_score == -1:
                return

            self.note_hit_or_missed = True

            if cur_score == 0:
                self.jth.add_to_q(0)
                self.miss.play()
                self.combo = 0
                return
            #Draws score text
            self.jth.add_to_q(cur_score)
            self.hit.play()

            self.combo += 1
            self.score += cur_score
            self.score_updated = True
            return

    def judge_ln_release(self, lane:int):
        if len(self.note_list[lane]) == 0:
            return

        note = self.note_list[lane][0]
        if not isinstance(note, LongNote):
            return
        #Checks if long note was being held the from before
        result = note.judge_release()
    def calculate_acc(self) -> float:
        return 100*(300*self.hits_300+200*self.hits_200+100*self.hits_100+50*self.hits_50)/(300*(self.hits_300+self.hits_200+self.hits_100+self.hits_50+self.miss_0))

#Just spawns some notes every 3 seconds
def note_test_wrapper():
    random_1 = randint(1,4)
    Note(random_1).draw()
    if randint(0,3) == 0:
        while 1:
            random_2 = randint(1,4)
            if random_1 != random_2:
                LongNote(random_2, 10)
                break

class JudgementTextHandler(Wait):
    '''
    Handles the text that appears when a note is judged.\n
    Has a feature where the note time gets shorter if there's a note hit while the text is on screen
    '''
    #In run(), check if q isn't empty
    #If it is, then set the time to MINIMUM_FRAME -1
    def __init__(self, g_manager:GameplayScriptManager) -> None:
        self.g_manager = g_manager
        self.game = g_manager.game
        self.scene = g_manager.game.cur_scene

        self.q = deque()
        self.to_stop_drawing = -1
        self.needed_time = -1
        self.to_draw = -1
        self.tick = lambda:self.scene.unpaused_ticks
        self.game.global_delta_time_list.append(self)
    def time_passed(self):
        if self.q and self.to_draw == -1:
            self.to_draw = self.q.popleft()
            self.needed_time = self.scene.unpaused_ticks + MAXMUM_JUDGEMENT_TEXT_FRAMES*FRAME_FREQUENCY
            if self.to_stop_drawing == -1:
                return True
            return False
        if self.needed_time == -1:
            return False
        if self.q:
            time_to_check = (MINIMUM_JUDGEMENT_TEXT_FRAMES-1)*FRAME_FREQUENCY
            if self.needed_time > time_to_check:
                self.needed_time = time_to_check
                return False
        return super().time_passed()
    def run(self):
        if self.to_stop_drawing == 0:
            self.g_manager.miss_text.stop_draw()
        if self.to_stop_drawing == 50:
            self.g_manager.bad_text.stop_draw()
        if self.to_stop_drawing == 100:
            self.g_manager.ok_text.stop_draw()
        if self.to_stop_drawing == 200:
            self.g_manager.good_text.stop_draw()
        if self.to_stop_drawing == 300:
            self.g_manager.excellent_text.stop_draw()
        self.to_stop_drawing = -1

        if self.to_draw == 0:
            self.g_manager.miss_text.draw()
            self.to_stop_drawing = 0
        elif self.to_draw == 50:
            self.g_manager.bad_text.draw()
            self.to_stop_drawing = 50
        elif self.to_draw == 100:
            self.g_manager.ok_text.draw()
            self.to_stop_drawing = 100
        elif self.to_draw == 200:
            self.g_manager.good_text.draw()
            self.to_stop_drawing = 200
        elif self.to_draw == 300:
            self.g_manager.excellent_text.draw()
            self.to_stop_drawing = 300
        self.to_draw = -1
        self.needed_time = self.scene.unpaused_ticks + MAXMUM_JUDGEMENT_TEXT_FRAMES*FRAME_FREQUENCY
    def add_to_q(self, judgement_value):
        self.q.append(judgement_value)

class AbstractNote(ABC):
    @abstractmethod
    def judge(self) -> int:
        pass

    @abstractmethod
    def move(self):
        pass

    @abstractmethod
    def q_destroy(self):
        pass

    @abstractmethod
    def destroy(self):
        pass

class Note(Sprite, AbstractNote):
    '''Class for not long notes'''
    def __init__(self, script_manager:GameplayScriptManager, key:int) -> None:
        '''Pos is the key needed'''
        self.script_manager = script_manager
        self.game = script_manager.game
        self.jth = script_manager.jth
        self.scene = script_manager.game.cur_scene

        self.pos = [360+200*key,0]
        self.key = key
        super().__init__(self.game, -8, self.pos, "note", origin=(0,0))
        self.draw()
        script_manager.note_list[key-1].append(self)
        self.tick_needed = TIME_NEEDED + self.scene.unpaused_ticks

    def move(self) -> None:
        '''Function that moves the note'''
        self.pos[1] += SCROLL_SPEED
        #Missed note
        if self.pos[1] > VERTICAL_SIZE:
            self.jth.add_to_q(0)
            self.script_manager.miss.play()
            self.q_destroy()

    def judge(self) -> int:
        '''
        Note judgment\n
        Returns judgement score, if the judgement is not in range, return -1\n
        If it is in range, destroy the note
        '''
        #Excellent
        if self._within_range(EXCELLENT_RANGE):
            self.destroy()
            self.hits_300 += 1
            return 300
        if self._within_range(GOOD_RANGE):
            self.destroy()
            self.hits_200 += 1
            return 200
        if self._within_range(OK_RANGE):
            self.destroy()
            self.hits_100 += 1
            return 100
        if self._within_range(BAD_RANGE):
            self.destroy()
            self.hits_50 += 1
            return 50
        if self._within_range(MISS_RANGE):
            self.miss_0 += 1
            return 0
        return -1

    def _within_range(self, range:int) -> bool:
        if self.tick_needed-range <= self.scene.unpaused_ticks <= self.tick_needed+range:
            return True
        return False

    def q_destroy(self):
        '''Queues the the note to be destroyed at the end of the frame'''
        self.scene.destroy_list.append(self)
        self.script_manager.note_hit_or_missed = True
        self.combo = 0
        self.miss_0 += 1

    def destroy(self):
        '''Removes itself from note and draw list'''
        self.script_manager.note_list[self.key-1].remove(self)
        self.scene.drawn_list.remove(self.to_send)

class LongNote(AbstractNote):
    '''Will maybe implement a minimum length for LNs'''
    def __init__(self, script_manger:GameplayScriptManager, key:int, duration:int) -> None:
        '''
        key (1-4) is the key the note is for\n
        duration (ms) is how long the note is
        '''

        self.script_manger = script_manger
        self.jth = script_manger.jth
        self.game = script_manger.game
        self.scene = script_manger.scene

        key_x = 360+NOTE_TEXTURE_LENGTH*key
        length = duration * SCROLL_SPEED
        self.key = key
        self.note_duration = duration
        self.tick_needed_bottom = TIME_NEEDED + self.scene.unpaused_ticks
        #Calculate how long the note is visually based off the length
        self.note_length = duration * SCROLL_SPEED
        self.bottom_note = Sprite(self.game, -7, [key_x,0], 'note')
        self.top_note = Sprite(self.game, -7, [key_x, -length], 'note')
        self.middle_rect = DrawbleRect(self.game, -8, [key_x+20, NOTE_TEXTURE_HEIGHT-length],
                                        (NOTE_TEXTURE_LENGTH-40, self.note_length), (255,255,255))
        #Note state
        self.note_failed = False
        self.bottom_note_scored = False
        
        self.bottom_note.draw()
        self.top_note.draw()
        self.middle_rect.draw()
        self.script_manger.note_list[key-1].append(self)

    @override
    def move(self) -> None:
        '''Function that moves the note'''
        self.top_note.pos[1] += SCROLL_SPEED
        self.bottom_note.pos[1] += SCROLL_SPEED
        self.middle_rect.pos[1] += SCROLL_SPEED
        #Missed note
        if self.top_note.pos[1] > VERTICAL_SIZE:
            self.jth.add_to_q(0)
            self.script_manger.miss.play()
            self.q_destroy()
            return
        if self.bottom_note.pos[1] > VERTICAL_SIZE and not self.bottom_note_scored:
            self.bottom_note_scored = True
            self.jth.add_to_q(0)
            self.script_manger.miss.play()

    def judge(self) -> int:
        '''
        Note judgment\n
        Returns judgement score, if the judgement is not in range, return -1\n
        If it is in range, destroy the note
        '''
        #Head already scored
        if self.bottom_note_scored:
            return -1
        #Excellent
        if self._within_range(EXCELLENT_RANGE):
            self.hits_300 += 1
            self.bottom_note_scored = True
            return 300
        if self._within_range(GOOD_RANGE):
            self.hits_200 += 1
            self.bottom_note_scored = True
            return 200
        if self._within_range(OK_RANGE):
            self.hits_100 += 1
            self.bottom_note_scored = True
            return 100
        if self._within_range(BAD_RANGE):
            self.hits_50 += 1
            self.bottom_note_scored = True
            return 50
        if self._within_range(MISS_RANGE):
            self.miss_0 += 1
            self.bottom_note_scored = True
            return 0
        return -1

    def _within_range(self, range:int) -> bool:
        if self.tick_needed_bottom-range <= self.scene.unpaused_ticks <= self.tick_needed_bottom+range:
            return True
        return False

    def judge_release(self):
        pass

    def q_destroy(self):
        self.scene.destroy_list.append(self)

    def destroy(self):
        self.scene.drawn_list.remove(self.bottom_note.to_send)
        self.scene.drawn_list.remove(self.top_note.to_send)
        self.scene.drawn_list.remove(self.middle_rect.to_send)
        self.script_manger.note_list[self.key-1].remove(self)
