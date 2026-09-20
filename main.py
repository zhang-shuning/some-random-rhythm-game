'''Main file for the game'''
# pylint: disable=no-member
from random import randint
import pygame

from modules.classes import Text, Wait, Sprite, WaitExtendable
from modules.constants import *
from modules.shared_variables import *
from modules.scripts import load_images, handle_fblits

#Pygame variable initialization
screen:pygame.Surface = pygame.display.set_mode((HORIZONTAL_SIZE, VERTICAL_SIZE),pygame.FULLSCREEN | pygame.SCALED)
clock:pygame.time.Clock = pygame.time.Clock()
pygame.init()
load_images()

import scenes.gameplay

scenes.gameplay.draw_assets()

#Just spawns some notes every 3 seconds
def note_test_wrapper():
    scenes.gameplay.Note(randint(1,4)).draw()

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
            scenes.gameplay.miss.play()
            return

        #Draws score text
        JTF.add_to_q(cur_score)
        scenes.gameplay.hit.play()

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

JTF = scenes.gameplay.JudgementTextHandler()

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
                scenes.gameplay.keypress.play()
            elif event.key == pygame.K_f:
                _judge_note(1)
                scenes.gameplay.keypress.play()
            elif event.key == pygame.K_j:
                _judge_note(2)
                scenes.gameplay.keypress.play()
            elif event.key == pygame.K_k:
                _judge_note(3)
                scenes.gameplay.keypress.play()

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
