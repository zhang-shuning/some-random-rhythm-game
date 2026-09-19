'''Main file for the game'''
# pylint: disable=no-member
from collections.abc import Callable
from collections import deque
import time
import pygame
from typing import Any, Callable

from modules.classes import Note, Text, Wait, Sprite, WaitExtendable
from modules.constants import *
from modules.shared_variables import *
from modules.scripts import load_images, handle_fblits

#Pygame variable initialization
screen:pygame.Surface = pygame.display.set_mode((HORIZONTAL_SIZE, VERTICAL_SIZE),pygame.FULLSCREEN | pygame.SCALED)
clock:pygame.time.Clock = pygame.time.Clock()
pygame.init()
load_images()

Sprite(-10, (HORIZONTAL_SIZE/2-400, 0), "chart").draw()
Sprite(-9, (HORIZONTAL_SIZE/2-400, VERTICAL_SIZE-JUDGEMENT_LINE_HEIGHT), "judgement_line").draw()

#Just spawns some notes every 3 seconds
def note_test_wrapper():
    Note(1).draw()
    Note(2).draw()
    Note(3).draw()
    Note(4).draw()

note_test_wrapper()
Wait(3, note_test_wrapper, repeats=True)

#Rhythm gaming!
def _judge_note(lane:int):
    if len(note_list[lane]) !=0:
        cur_score = note_list[lane][0].judge()
        #Handle point scoring
        if cur_score == -1:
            return
        if cur_score == 0:
            miss_text.draw(True)
            return

        #Note in range and hit
        if cur_score == 300:
            pass
            #excellent_text.draw(True)
        elif cur_score == 200:
            good_text.draw(True)
        elif cur_score == 100:
            ok_text.draw(True)
        elif cur_score == 50:
            bad_text.draw(True)

        Counters.score += cur_score
        Flags.score_updated = True

hit_lights:list[list[Sprite|WaitExtendable]] = [[Sprite(-8.5, (560+200*x, VERTICAL_SIZE-300), "hit_light")] for x in range(4)]
for i in hit_lights:
    i.append(WaitExtendable(HITLIGHT_DISABLE_TIME, i[0].stop_draw))

def _enable_hitlight(n):
    hit_lights[n][1].set_time()
    if not hit_lights[n][0].is_drawn:
        hit_lights[n][0].draw()

#Text declaration
mouse_text = Text("", (HORIZONTAL_SIZE-200,0), 100)
fps_text = Text("0", (0, 0), 100)
score_text = Text("score: 0", (0, 25), 100)
score_text.draw()

excellent_text = Text("Excellent", JUDEMENT_TEXT_POS, 10, font_size=100, text_color=(0, 150, 255))
good_text = Text("Good", JUDEMENT_TEXT_POS, 10, font_size=100, text_color=(34, 139, 34))
ok_text = Text("OK", JUDEMENT_TEXT_POS, 10, font_size=100, text_color=(175, 225, 175))
bad_text = Text("Bad", JUDEMENT_TEXT_POS, 10, font_size=100, text_color=(211, 211, 211))
miss_text = Text("Miss!", JUDEMENT_TEXT_POS, 10, font_size=200, text_color=(255, 0, 0))

class JudgementTextHandler(Wait):
    #In run(), check if q isn't empty
    #If it is, then set the time to MINIMUM_FRAME -1
    def __init__(self) -> None:
        self.q = deque()
        self.buf = -2
        self.needed_time = -1
        delta_time_list.append(self)
    def time_passed(self):
        #Check if queue has a value in it, if it does, shorten the text
        if self.q:
            if self.buf != -2:
                time_to_set = (MINIMUM_JUDGEMENT_TEXT_FRAMES-1)*FRAME_FREQUENCY+Counters.ticks
                if self.needed_time <= time_to_set:
                    return super().time_passed()
                self.needed_time = time_to_set
            else:
                self.buf = self.q.popleft()
                self.needed_time = self.delta*TPS_CAP + Counters.ticks
            return False
        if self.buf == -2:
            return False
        return super().time_passed()
    def run(self):
        #Removed the buffered text, set buf to -2
        if self.buf == 0:
            miss_text.stop_draw()
        if self.buf == 50:
            miss_text.stop_draw()
        if self.buf == 100:
            miss_text.stop_draw()
        if self.buf == 200:
            miss_text.stop_draw()
        if self.buf == 300:
            miss_text.stop_draw()

        if self.buf == 0:
            miss_text.draw()
        if self.buf == 50:
            miss_text.draw()
        if self.buf == 100:
            miss_text.draw()
        if self.buf == 200:
            miss_text.draw()
        if self.buf == 300:
            miss_text.draw()

        self.buf = -2
    def add_to_q(self, judgement_value):
        self.q.append(judgement_value)

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
                print(pygame.mouse.get_pos())
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                Flags.running = False
            elif event.key == pygame.K_d:
                _judge_note(0) 
            elif event.key == pygame.K_f:
                _judge_note(1)
            elif event.key == pygame.K_j:
                _judge_note(2)
            elif event.key == pygame.K_k:
                _judge_note(3)

    #Held keys
    keys = pygame.key.get_pressed()
    #Only check if the frame is being drawn for hitlights because hitlights are rendered
    if Counters.ticks % FRAME_FREQUENCY == 0:
        if keys[pygame.K_d]:
            _enable_hitlight(0)
        if keys[pygame.K_f]:
            _enable_hitlight(1)
        if keys[pygame.K_j]:
            _enable_hitlight(2)
        if keys[pygame.K_k]:
            _enable_hitlight(3)

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

        pygame.display.flip()

    #Next tick
    Counters.ticks+=1
    clock.tick(TPS_CAP)
