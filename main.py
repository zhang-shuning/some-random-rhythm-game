'''Main file for the game'''
# pylint: disable=no-member
import time
import pygame
import pathlib
from typing import TYPE_CHECKING

from modules.classes import Text, Wait, Scene
from modules.constants import *
from modules.scripts import handle_fblits

from scenes.gameplay_scripts import GameplayScriptManager
from scenes.gameplay import GameplayScene
from scenes.level_selector import LevelSelectScene
from scenes.main_menu import MainMenuScene
from scenes.map_maker import MapMakerScene
from scenes.replay import ReplayScene

#Pygame variable initialization
screen:pygame.Surface = pygame.display.set_mode((HORIZONTAL_SIZE, VERTICAL_SIZE),pygame.FULLSCREEN | pygame.SCALED)
clock:pygame.time.Clock = pygame.time.Clock()
pygame.init()


class GameController():
    def __init__(self) -> None:
        self.load_images()
        self.init_scenes()

        self.cur_scene = LevelSelectScene()

        #Initialization stuff
        self.next_scene_str = ""
        self.running = True
        self.new_scene = True
        self.ticks = 0

        #Text declaration
        self.fps_text = Text(self, "this is the fps", (HORIZONTAL_SIZE, 0), 100, origin=(1,0))

        def fps_wrapper():
            self.fps_text.update_and_draw_text(f"{clock.get_fps():.5f}")
        self.fps_text.draw()
        Wait(self, .1, fps_wrapper, repeats=True, is_global=True)

        #This system checks if a note is out sync with the actual time
        self.expected_time = time.time()
        self.cur_time = time.time()
        self.ticks_to_increment = 1

        #Global lists
        self.images_dict = {} #The images dict stores all textures in the game; not dynamically loaded for now
        self.global_delta_time_list = []
        self.global_draw_list = []
        self.scene_name_dict = {}
        self.button_list = []

    def _load_image(self, image_path:str|pathlib.Path, texture_name:str, transparent=False):
        '''Loads a single image and saves to dictionary based from filename'''
        if not transparent:
            self.images_dict[texture_name] = pygame.image.load(image_path).convert()
        else:
            self.images_dict[texture_name] = pygame.image.load(image_path).convert_alpha()

    def load_images(self) -> None:
        '''Loads all images and saves them to a dictionary'''
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

    def init_scenes(self) -> None:
        '''Hard coded because... I really couldn't think of anything better at the time'''
        self.scene_name_dict = {
            
        }
    def run(self):
        '''Runs the main loop of the game'''
        #Main loop
        while self.running:
            if self.new_scene:
                self.cur_scene.scene_cleanup()
                self.cur_scene = self.scene_name_dict[self.cur_scene]
                self.cur_scene.init_scene()
                self.new_scene = False

            self.fps_text.draw()

        assert isinstance(self.cur_scene, Scene)
        #Get events
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                #Button check
                for i in self.button_list:
                    if i[0].collidepoint(event.pos):
                        i[1]()

            self.cur_scene.handle_event(event)

        #Held keys
        keys = pygame.key.get_pressed()
        self.cur_scene.handle_held_keys(keys)

        #Get delta time events
        for i in self.global_delta_time_list:
            if i.time_passed():
                i.run()

        self.cur_scene.pre_render()

        #Render
        if self.ticks % FRAME_FREQUENCY == 0:
            self.cur_scene.render(screen)
            screen.fblits(handle_fblits(self.global_draw_list))
            pygame.display.flip()

        #If time is too off the expected time, go multiple ticks instead
        self.expected_time += S_PER_TICK
        cur_time = time.time()

        #Check frame drops
        if cur_time > self.expected_time:
            #Calculate how many ticks the time has gone up by
            ticks_to_increment = int((cur_time-self.expected_time) / S_PER_TICK)
            self.expected_time += ticks_to_increment*S_PER_TICK

        #Next tick
        self.cur_scene.tick()
        self.ticks+=1

        clock.tick(TPS_CAP)
