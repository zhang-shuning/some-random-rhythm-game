'''Temporary text console'''

import pygame

from main import GameController
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

class LevelSelectScene(Scene)
    def __init__(self, game: GameController) -> None:
        super().__init__(game)
        self.intro_text = Text(game, intro_string, (0,0), 10, 30)
        self.text_box = Text(game, "", (0, 200), 10)

    def run_command(self, command:str):
        if command == "exit":
            self.game.running = False
        elif command == "back":
            self.game.new_scene = True
            self.game.next_scene_str = "main_menu"
        elif command == "1":
            self.game.new_scene = True
            self.game.next_scene_str = "gameplay"
        elif command == '2':
            self.game.new_scene = True
            self.game.next_scene_str = "replay"

    def event_handler(self, event:pygame.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.running = False
            elif event.key == pygame.K_BACKSPACE and (event.mod & pygame.KMOD_CTRL):
                self.text_box.update_and_draw_text("")
            elif event.key == pygame.K_BACKSPACE:
                self.text_box.update_and_draw_text(self.text_box.text[:-1])
            elif event.key == pygame.K_RETURN:
                self.run_command(self.text_box.text)
                self.text_box.update_and_draw_text("")
        elif event.type == pygame.TEXTINPUT:
            self.text_box.update_and_draw_text(self.text_box.text + event.text)


    def render(self, screen):
        screen.fill((152,100,0))
        screen.fblits(handle_fblits(self.fblits_list))

    def scene_init(self):
        self.intro_text.draw()
        self.text_box.draw()