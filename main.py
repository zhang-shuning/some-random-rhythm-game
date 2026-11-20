'''Main file for the game'''
# pylint: disable=no-member
import time
import pygame
import pathlib

from modules.classes import Text, Wait, Scene
from modules.constants import *
from modules.scripts import handle_fblits

from scenes.gameplay import GameplayScene
from scenes.level_selector import LevelSelectScene
from scenes.main_menu import MainMenuScene
from scenes.map_maker import MapMakerScene
from scenes.replay import ReplayScene

#Pygame variable initialization
screen:pygame.Surface = pygame.display.set_mode((HORIZONTAL_SIZE, VERTICAL_SIZE),pygame.FULLSCREEN | pygame.SCALED)
clock:pygame.time.Clock = pygame.time.Clock()

class GameController():
    def __init__(self) -> None:
        #Global lists
        self.images_dict = {} #The images dict stores all textures in the game; not dynamically loaded for now
        self.global_delta_time_list = []
        self.global_draw_list = []
        self.button_list = []

        #Initialization
        pygame.init()
        self._load_images()
        self._init_scenes()

        self._next_scene_str = "main_menu"
        self._new_scene = True
        self.running = True
        self.ticks = 0

        #Text declaration
        self.fps_text = Text(self, "this is the fps", (HORIZONTAL_SIZE, 0), 100, origin=(1,0), is_global=True)

        def _fps_wrapper():
            self.fps_text.update_and_draw_text(f"{clock.get_fps():.5f}")
        self.fps_text.draw()
        Wait(self, .1, _fps_wrapper, repeats=True, is_global=True)

        #This system checks if a note is out sync with the actual time
        self._expected_time = time.time()
        self._cur_time = time.time()
        self._ticks_to_increment = 1

        self._cur_scene:Scene = Scene(self)

    def _load_image(self, image_path:str|pathlib.Path, texture_name:str, transparent=False):
        '''Helper method that loads a single image and saves to the dictionary based from filename'''
        if not transparent:
            self.images_dict[texture_name] = pygame.image.load(image_path).convert()
        else:
            self.images_dict[texture_name] = pygame.image.load(image_path).convert_alpha()

    def _load_images(self) -> None:
        '''
        Loads all images and saves them to a dictionary
        For now, all textures are loaded immediately, but dynamic loading could come later
        if memory ever becomes an issue
        '''
        print("Loading images...")
        textures_folder = pathlib.Path("assets/textures")
        transparent_texture_folder = pathlib.Path("assets/textures-transparent")

        for item in textures_folder.rglob("*"):
            if item.is_file() and item.suffix in IMAGE_FILE_EXTENSIONS:
                print(item.name)
                self._load_image(item, item.stem)
        
        for item in transparent_texture_folder.rglob("*"):
            if item.is_file() and item.suffix in IMAGE_FILE_EXTENSIONS:
                print(item.name)
                self._load_image(item, item.stem, transparent=True)

    def _init_scenes(self) -> None:
        '''Hard coded because the scenes need to be switched either after or directly directly before...
        and I really couldn't think of anything better at the time'''
        self.scene_name_dict= {
            "gameplay" : GameplayScene,
            "level_selector" : LevelSelectScene,
            "main_menu" : MainMenuScene,
            "map_maker" : MapMakerScene,
            "replay" : ReplayScene
        }

    def load_scene(self, scene:str):
        self._new_scene = True
        self._next_scene_str = scene

    def run(self):
        '''Runs the main loop of the game'''
        #Main loop
        while self.running:
            if self._new_scene:
                self._cur_scene = self.scene_name_dict[self._next_scene_str](self)
                print(f"initializing {self._cur_scene}")
                self.button_list.clear()
                self._cur_scene.scene_init()
                self._new_scene = False

            assert isinstance(self._cur_scene, Scene)
            #Get events
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    #Button check
                    for i in self.button_list:
                        if i[0].collidepoint(event.pos):
                            i[1]()

                self._cur_scene.handle_event(event)

            #Held keys
            keys = pygame.key.get_pressed()
            self._cur_scene.handle_held_keys(keys)

            #Get delta time events
            for i in self.global_delta_time_list:
                if i.time_passed():
                    i.run()

            self._cur_scene.pre_render()

            #Render
            self._cur_scene.render(screen)
            screen.fblits(handle_fblits(self.global_draw_list))
            pygame.display.flip()

            #If time is too off the expected time, go multiple ticks instead
            self._expected_time += S_PER_TICK
            _cur_time = time.time()

            #Check frame drops
            if _cur_time > self._expected_time:
                #Calculate how many ticks the time has gone up by
                _ticks_to_increment = int((_cur_time-self._expected_time) / S_PER_TICK)
                self._expected_time += _ticks_to_increment*S_PER_TICK
            
            #Next tick
            #print(self.ticks, self.global_delta_time_list)
            self._cur_scene.tick()
            self.ticks+=1

            clock.tick(TPS_CAP)

if __name__ == "__main__":
    GameController().run()