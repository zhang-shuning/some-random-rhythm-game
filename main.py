'''Main file for the game'''
# pylint: disable=no-member
from collections.abc import Callable
from collections import deque
from random import randint
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
    Note(randint(1,4)).draw()

note_test_wrapper()
Wait(.25, note_test_wrapper, repeats=True)

#Rhythm gaming!
def _judge_note(lane:int):
    if len(note_list[lane]) !=0:
        cur_score = note_list[lane][0].judge()
        #Handle point scoring
        if cur_score == -1:
            return
        if cur_score == 0:
            JTF.add_to_q(0)
            return

        #Note in range and hit
        if cur_score == 300:
            pass
            #excellent_text.draw(True)
        else:
            JTF.add_to_q(cur_score)

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
        print("ran")
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
            miss_text.draw(True)
            self.to_stop_drawing = 0
        elif self.to_draw == 50:
            bad_text.draw(True)
            self.to_stop_drawing = 50
        elif self.to_draw == 100:
            ok_text.draw(True)
            self.to_stop_drawing = 100
        elif self.to_draw == 200:
            good_text.draw(True)
            self.to_stop_drawing = 200
        elif self.to_draw == 300:
            excellent_text.draw(True)
            self.to_stop_drawing = 300
        self.to_draw = -1
        self.needed_time = Counters.ticks + MAXMUM_JUDGEMENT_TEXT_FRAMES*FRAME_FREQUENCY
    def add_to_q(self, judgement_value):
        self.q.append(judgement_value)

JTF = JudgementTextHandler()

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
                print(f"mouse pos {pygame.mouse.get_pos()}")
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
            score_text.update_and_draw_text(f"{Counters.score} q {JTF.q}")
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
