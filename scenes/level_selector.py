'''Temporary text console'''

import pygame

from modules.classes import Scene, Text
from modules.scripts import handle_fblits
from modules.shared_variables import *
from modules.constants import *

intro_text = Text("This is a hopefully temporary text based console", (0,0), 10, 30)
text_box = Text("", (0, 200), 10)

def event_handler(event:pygame.Event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            Flags.running = False
        elif event.key == pygame.K_BACKSPACE:
            text_box.update_and_draw_text(text_box.text[:-1])
    elif event.type == pygame.TEXTINPUT:


def render(screen):
    if Counters.ticks % FRAME_FREQUENCY == 0:
        screen.fill((152,100,0))
        handle_fblits()
        screen.fblits(fblits_list)
        pygame.display.flip()

def scene_init():
    intro_text.draw()
    text_box.draw()

scene = Scene("level_selector", event_handler=event_handler,
               render=render, scene_init_function=scene_init)