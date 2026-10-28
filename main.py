'''Main file for the game'''
# pylint: disable=no-member
import time
import pygame
from typing import TYPE_CHECKING

from modules.classes import Text, Wait, Scene
from modules.constants import *
from modules.shared_variables import *
from modules.scripts import load_images

from scenes.gameplay_scripts import GameplayScriptManager

#Pygame variable initialization
screen:pygame.Surface = pygame.display.set_mode((HORIZONTAL_SIZE, VERTICAL_SIZE),pygame.FULLSCREEN | pygame.SCALED)
clock:pygame.time.Clock = pygame.time.Clock()
pygame.init()
load_images()

from scenes.init_scenes import init_scenes
init_scenes()

class GameController():
    def __init__(self) -> None:
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
        self.cur_scene.render(screen)

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
