'''Main file for the game'''
# pylint: disable=no-member
import time
import pygame

from modules.classes import Note, Text, Wait, Sprite
from modules.constants import *
from modules.shared_variables import *
from modules.scripts import load_images, handle_fblits

#Pygame variable initialization
screen:pygame.Surface = pygame.display.set_mode((HORIZONTAL_SIZE, VERTICAL_SIZE),pygame.FULLSCREEN | pygame.SCALED)
clock:pygame.time.Clock = pygame.time.Clock()
pygame.init()
load_images()

#Sprite(-1, (HORIZONTAL_SIZE/4, 0), "test").draw()
Sprite(-10, (HORIZONTAL_SIZE/2-400, 0), "chart").draw()
Sprite(-9, (HORIZONTAL_SIZE/2-400, VERTICAL_SIZE-JUDGEMENT_LINE_HEIGHT), "judgement_line").draw()

def note_test_wrapper():
    Note(1).draw()
    Note(2).draw()
    Note(3).draw()
    Note(4).draw()

note_test_wrapper()

Wait(3, note_test_wrapper, True)

#Rhythm gaming!
def _judge_note(lane:int):
    if len(note_list[lane]) !=0:
        cur_score = note_list[lane][0].judge()
        if cur_score != -1:
            Counters.score += cur_score
            Flags.score_updated = True

#Text declaration
mouse_text = Text("", (HORIZONTAL_SIZE-200,0), 100)
fps_text = Text("0", (0, 0), 100)
score_text = Text("score: 0", (0, 25), 100)

score_text.draw()
def fps_wrapper(): fps_text.update_and_draw_text(str(clock.get_fps()))
fps_text.draw()
fps_update = Wait(.1, fps_wrapper, True)

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

    #Get delta time events
    for i in delta_time_list:
        if i.is_true():
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
