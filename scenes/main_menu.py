from main import GameController
from modules.classes import *
from modules.scripts import handle_fblits

pygame.font.init()

class MainMenuScene(Scene):
    def __init__(self, game: GameController) -> None:
        super().__init__(game)
        self.background = Sprite(game, -1, (0,0), "title_image")
        self.play_button = Button(game, "Play Game", (1100,300), 10, rect_size=(500,100),
                                   rect_color=(100,100,0), on_press=self.goto_level_select)
        self.settings_button = Button(game, "Settings", (1100,550), 10, rect_size=(500,100))
        self.exit_button = Button(game, "Exit Game", (1100,800), 10, rect_size=(500,100),
                                   on_press=self.exit_game, rect_color=(0,100,100))

        self.main_menu_elements = (self.play_button, self.settings_button, self.exit_button, self.background)

    def init(self):
        for element in self.main_menu_elements: 
            element.draw()

    def event_handler(self, event:pygame.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.running = False

    def render(self, screen):
        screen.fill((152,100,0))
        screen.fblits(handle_fblits(self.fblits_list))

    def goto_level_select(self):
        self.game.new_scene = True
        self.game.next_scene_str = "level_selector"

    def exit_game(self):
        self.running = False
