'''Temporary text console'''

import pygame

from modules.classes import Scene, Text
from modules.scripts import handle_fblits
from modules.constants import *

intro_string = '''
This is a (hopefully) temporary text based console.
So far:
1 goes to game
2 goes to replay test
exit closes the program
back goes back to main menu
'''

intro_text = Text(intro_string, (0,0), 10, 30)
text_box = Text("", (0, 200), 10)

def run_command(command:str):
    if command == "exit":
        Flags.running = False
    elif command == "back":
        Flags.new_scene = True
        self.game.next_scene_str = "main_menu"
    elif command == "1":
        Flags.new_scene = True
        self.game.next_scene_str = "gameplay"
    elif command == '2':
        Flags.new_scene = True
        self.game.next_scene_str = "replay"

def event_handler(event:pygame.Event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            Flags.running = False
        elif event.key == pygame.K_BACKSPACE and (event.mod & pygame.KMOD_CTRL):
            text_box.update_and_draw_text("")
        elif event.key == pygame.K_BACKSPACE:
            text_box.update_and_draw_text(text_box.text[:-1])
        elif event.key == pygame.K_RETURN:
            run_command(text_box.text)
            text_box.update_and_draw_text("")
    elif event.type == pygame.TEXTINPUT:
        text_box.update_and_draw_text(text_box.text + event.text)


def render(screen):
    if Counters.ticks % FRAME_FREQUENCY == 0:
        screen.fill((152,100,0))
        handle_fblits()
        screen.fblits(fblits_list)
        pygame.display.flip()

def scene_init():
    intro_text.draw()
    text_box.draw()

def make_scene():
    scene = Scene("level_selector", event_handler=event_handler,
                render=render, scene_init_function=scene_init)