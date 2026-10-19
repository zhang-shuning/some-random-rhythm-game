from collections import deque
from abc import ABC, abstractmethod
from typing import override

import pygame

from modules.scripts import handle_fblits
from modules.classes import Wait, Text, Sprite, WaitExtendable, DrawbleRect
from modules.constants import *
from modules.shared_variables import *

#SFX
hit = pygame.Sound("assets/sfx/hit.wav")
keypress = pygame.Sound("assets/sfx/keypress.wav")
miss = pygame.Sound("assets/sfx/miss.wav")

hit.set_volume(.1)
keypress.set_volume(.2)
miss.set_volume(.6)

#Sprites
chart = Sprite(-10, (HORIZONTAL_SIZE/2-400, 0), "chart")
judgement_line = Sprite(-9, (HORIZONTAL_SIZE/2-400, VERTICAL_SIZE-JUDGEMENT_LINE_HEIGHT), "judgement_line")

#Text
excellent_text = Text("Excellent", JUDEMENT_TEXT_POS, 10, font_size=120, text_color=(0, 150, 255), origin=(.5,.5))
good_text = Text("Good", JUDEMENT_TEXT_POS, 10, font_size=150, text_color=(34, 139, 34), origin=(.5,.5))
ok_text = Text("OK", JUDEMENT_TEXT_POS, 10, font_size=150, text_color=(175, 225, 175), origin=(.5,.5))
bad_text = Text("Bad", JUDEMENT_TEXT_POS, 10, font_size=150, text_color=(211, 211, 211), origin=(.5,.5))
miss_text = Text("Miss!", JUDEMENT_TEXT_POS, 10, font_size=150, text_color=(255, 0, 0), origin=(.5,.5))
mouse_text = Text("", (HORIZONTAL_SIZE-500,0), 100)
score_text = Text("0", (HORIZONTAL_SIZE, 25), 100, font_size=40, origin=(1,0))
acc_text = Text("100.00%", (HORIZONTAL_SIZE, 60), 100, font_size=40, origin=(1,0))
combo_text = Text("0", (0, VERTICAL_SIZE), 100, font_size=100, origin=(0,1))

#Input array
input_array = []

def events(event: pygame.Event):
    if event.type == pygame.QUIT:
        #I shouldn't need any cleanup after quit, so I should be able to keep this
        #For all scenes
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
    if Counters.game_ticks % FRAME_FREQUENCY == 0:
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

def after_render():
    pass

def scene_init():
    pass

Scene(events, held_keys, render, after_render, scene_init)


class JudgementTextHandler(Wait):
    '''
    Handles the text that appears when a note is judged.\n
    Has a feature where the note time gets shorter if there's a note hit while the text is on screen
    '''
    #In run(), check if q isn't empty
    #If it is, then set the time to MINIMUM_FRAME -1
    def __init__(self) -> None:
        self.q = deque()
        self.to_stop_drawing = -1
        self.needed_time = -1
        self.to_draw = -1
        self.tick = lambda:Counters.game_ticks
        delta_time_list.append(self)
    def time_passed(self):
        if self.q and self.to_draw == -1:
            self.to_draw = self.q.popleft()
            self.needed_time = Counters.game_ticks + MAXMUM_JUDGEMENT_TEXT_FRAMES*FRAME_FREQUENCY
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
            miss_text.stop_draw()
        if self.to_stop_drawing == 50:
            bad_text.stop_draw()
        if self.to_stop_drawing == 100:
            ok_text.stop_draw()
        if self.to_stop_drawing == 200:
            good_text.stop_draw()
        if self.to_stop_drawing == 300:
            excellent_text.stop_draw()
        self.to_stop_drawing = -1

        if self.to_draw == 0:
            miss_text.draw()
            self.to_stop_drawing = 0
        elif self.to_draw == 50:
            bad_text.draw()
            self.to_stop_drawing = 50
        elif self.to_draw == 100:
            ok_text.draw()
            self.to_stop_drawing = 100
        elif self.to_draw == 200:
            good_text.draw()
            self.to_stop_drawing = 200
        elif self.to_draw == 300:
            excellent_text.draw()
            self.to_stop_drawing = 300
        self.to_draw = -1
        self.needed_time = Counters.game_ticks + MAXMUM_JUDGEMENT_TEXT_FRAMES*FRAME_FREQUENCY
    def add_to_q(self, judgement_value):
        self.q.append(judgement_value)

JTF = JudgementTextHandler()

class AbstractNote(ABC):
    @abstractmethod
    def judge(self):
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
    def __init__(self, key:int) -> None:
        '''Pos is the key needed'''
        self.pos = [360+200*key,0]
        self.key = key
        super().__init__(-8, self.pos, "note", origin=(0,0))
        self.draw()
        note_list[key-1].append(self)
        self.tick_needed = TIME_NEEDED + Counters.game_ticks

    def move(self) -> None:
        '''Function that moves the note'''
        self.pos[1] += SCROLL_SPEED
        #Missed note
        if self.pos[1] > VERTICAL_SIZE:
            JTF.add_to_q(0)
            miss.play()
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
            Counters._300 += 1
            return 300
        if self._within_range(GOOD_RANGE):
            self.destroy()
            Counters._200 += 1
            return 200
        if self._within_range(OK_RANGE):
            self.destroy()
            Counters._100 += 1
            return 100
        if self._within_range(BAD_RANGE):
            self.destroy()
            Counters._50 += 1
            return 50
        if self._within_range(MISS_RANGE):
            Counters.miss += 1
            return 0
        return -1

    def _within_range(self, range:int) -> bool:
        if self.tick_needed-range <= Counters.game_ticks <= self.tick_needed+range:
            return True
        return False

    def q_destroy(self):
        '''Queues the the note to be destroyed at the end of the frame'''
        destroy_list.append(self)
        Flags.note_hit_or_missed = True
        Counters.combo = 0
        Counters.miss += 1

    def destroy(self):
        '''Removes itself from note and draw list'''
        note_list[self.key-1].remove(self)
        drawn_list.remove(self.to_send)

class LongNote(AbstractNote):
    '''Will maybe implement a minimum length for LNs'''
    def __init__(self, key, duration) -> None:
        '''
        key (1-4) is the key the note is for\n
        duration (ms) is how long the note is
        '''
        key_x = 360+NOTE_TEXTURE_LENGTH*key
        length = duration * SCROLL_SPEED
        self.key = key
        self.note_duration = duration
        self.tick_needed_bottom = TIME_NEEDED + Counters.game_ticks
        #Calculate how long the note is visually based off the length
        self.note_length = duration * SCROLL_SPEED
        self.bottom_note = Sprite(-7, [key_x,0], 'note')
        self.top_note = Sprite(-7, [key_x, -length], 'note')
        self.middle_rect = DrawbleRect(-8, [key_x+20, NOTE_TEXTURE_HEIGHT-length],
                                        (NOTE_TEXTURE_LENGTH-40, self.note_length), (255,255,255))
        #Note state
        self.note_failed = False
        self.bottom_note_scored = False
        
        self.bottom_note.draw()
        self.top_note.draw()
        self.middle_rect.draw()
        note_list[key-1].append(self)

    @override
    def move(self) -> None:
        '''Function that moves the note'''
        self.top_note.pos[1] += SCROLL_SPEED
        self.bottom_note.pos[1] += SCROLL_SPEED
        self.middle_rect.pos[1] += SCROLL_SPEED
        #Missed note
        if self.top_note.pos[1] > VERTICAL_SIZE:
            JTF.add_to_q(0)
            miss.play()
            self.q_destroy()
            return
        if self.bottom_note.pos[1] > VERTICAL_SIZE and not self.bottom_note_scored:
            self.bottom_note_scored = True
            JTF.add_to_q(0)
            miss.play()

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
            Counters._300 += 1
            self.bottom_note_scored = True
            return 300
        if self._within_range(GOOD_RANGE):
            Counters._200 += 1
            self.bottom_note_scored = True
            return 200
        if self._within_range(OK_RANGE):
            Counters._100 += 1
            self.bottom_note_scored = True
            return 100
        if self._within_range(BAD_RANGE):
            Counters._50 += 1
            self.bottom_note_scored = True
            return 50
        if self._within_range(MISS_RANGE):
            Counters.miss += 1
            self.bottom_note_scored = True
            return 0
        return -1

    def _within_range(self, range:int) -> bool:
        if self.tick_needed_bottom-range <= Counters.game_ticks <= self.tick_needed_bottom+range:
            return True
        return False

    def judge_release(self):
        pass

    def q_destroy(self):
        destroy_list.append(self)

    def destroy(self):
        print(f"bottom {self.bottom_note in drawn_list}")
        print(f"top {self.top_note in drawn_list}")
        print(f"middle {self.middle_rect in drawn_list}")
        drawn_list.remove(self.bottom_note.to_send)
        drawn_list.remove(self.top_note.to_send)
        drawn_list.remove(self.middle_rect.to_send)
        note_list[self.key-1].remove(self)

def calculate_acc():
    Counters.acc = 100*(300*Counters._300+200*Counters._200+100*Counters._100+50*Counters._50)/(300*(Counters._300+Counters._200+Counters._100+Counters._50+Counters.miss))

def judge_note(lane:int):
    if len(note_list[lane]) == 0:
        return

    note = note_list[lane][0]
    if isinstance(note, AbstractNote):
        cur_score = note.judge()
        #Handle point scoring
        if cur_score == -1:
            return

        Flags.note_hit_or_missed = True

        if cur_score == 0:
            JTF.add_to_q(0)
            miss.play()
            Counters.combo = 0
            return
        #Draws score text
        JTF.add_to_q(cur_score)
        hit.play()

        Counters.combo += 1
        Counters.score += cur_score
        Flags.score_updated = True
        return

def judge_ln_release(lane:int):
    if len(note_list[lane]) == 0:
        return

    note = note_list[lane][0]
    if not isinstance(note, LongNote):
        return
    #Checks if long note was being held the from before
    result = note.judge_release()

hit_lights:list[list[Sprite|WaitExtendable]] = [[Sprite(-8.5, (560+200*x, VERTICAL_SIZE-250), "hit_light")] for x in range(4)]
for i in hit_lights:
    i.append(WaitExtendable(HITLIGHT_DISABLE_TIME, i[0].stop_draw))
def enable_hitlight(n):
    '''Enables the hitlight'''
    hit_lights[n][1].set_time()
    if not hit_lights[n][0].is_drawn:
        hit_lights[n][0].draw()

def draw_assets():
    chart.draw()
    judgement_line.draw()

def stop_assets():
    chart.stop_draw()
    judgement_line.stop_draw()
    note_list.clear()
