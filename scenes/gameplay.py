from collections import deque

import pygame

from modules.classes import Wait, Text, Sprite, WaitExtendable
from modules.constants import *
from modules.shared_variables import *

#SFX
hit = pygame.Sound("assets/sfx/hit.wav")
keypress = pygame.Sound("assets/sfx/keypress.wav")
miss = pygame.Sound("assets/sfx/miss.wav")

hit.set_volume(.15)
keypress.set_volume(.25)
miss.set_volume(.4)


chart = Sprite(-10, (HORIZONTAL_SIZE/2-400, 0), "chart")
judgement_line = Sprite(-9, (HORIZONTAL_SIZE/2-400, VERTICAL_SIZE-JUDGEMENT_LINE_HEIGHT), "judgement_line")

excellent_text = Text("Excellent", JUDEMENT_TEXT_POS, 10, font_size=100, text_color=(0, 150, 255), origin=(.5,.5))
good_text = Text("Good", JUDEMENT_TEXT_POS, 10, font_size=100, text_color=(34, 139, 34), origin=(.5,.5))
ok_text = Text("OK", JUDEMENT_TEXT_POS, 10, font_size=100, text_color=(175, 225, 175), origin=(.5,.5))
bad_text = Text("Bad", JUDEMENT_TEXT_POS, 10, font_size=100, text_color=(211, 211, 211), origin=(.5,.5))
miss_text = Text("Miss!", JUDEMENT_TEXT_POS, 10, font_size=200, text_color=(255, 0, 0), origin=(.5,.5))

class JudgementTextHandler(Wait):
    '''Handles the text that appears when a note is judged.'''
    #In run(), check if q isn't empty
    #If it is, then set the time to MINIMUM_FRAME -1
    def __init__(self) -> None:
        self.q = deque()
        self.to_stop_drawing = -1
        self.needed_time = -1
        self.to_draw = -1
        delta_time_list.append(self)
    def time_passed(self):
        if self.q and self.to_draw == -1:
            self.to_draw = self.q.popleft()
            self.needed_time = Counters.ticks + MAXMUM_JUDGEMENT_TEXT_FRAMES*FRAME_FREQUENCY
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
        self.needed_time = Counters.ticks + MAXMUM_JUDGEMENT_TEXT_FRAMES*FRAME_FREQUENCY
    def add_to_q(self, judgement_value):
        self.q.append(judgement_value)

JTF = JudgementTextHandler()

class Note(Sprite):
    '''Class for not long notes'''
    def __init__(self, key:int) -> None:
        '''Pos is the key needed'''
        self.pos = [360+200*key,0]
        self.key = key
        super().__init__(-8, self.pos, "note", origin=(0,0))
        self.draw()
        note_list[key-1].append(self)
        self.tick_needed = TIME_NEEDED + Counters.ticks

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
        if self.tick_needed-range <= Counters.ticks <= self.tick_needed+range:
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

def calculate_acc():
    Counters.acc = 100*(300*Counters._300+200*Counters._200+100*Counters._300+50*Counters._50)/(300*(Counters._300+Counters._200+Counters._100+Counters._50+Counters.miss))

def judge_note(lane:int):
    if len(note_list[lane]) !=0:
        cur_score = note_list[lane][0].judge()
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

hit_lights:list[list[Sprite|WaitExtendable]] = [[Sprite(-8.5, (560+200*x, VERTICAL_SIZE-300), "hit_light")] for x in range(4)]
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
