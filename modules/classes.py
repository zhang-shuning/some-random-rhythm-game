'''This file contains the classes used in the game!'''

from typing import override
from collections.abc import Callable
import logging
import pygame

from modules.shared_variables import delta_time_list, Flags, Counters, drawn_list, images_dict, note_list
from modules.constants import *

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

class DrawnEntity():
    '''This is the base class for all entities that get drawn on screen.'''
    def __init__(self, priority, pos) -> None:
        self.pos = pos
        self.priority = priority
        self.entities = [] # Ordered so first thing appended is first
        self.to_send = ([], 0)
        self.setup()
    def setup(self) -> None:
        '''Doesn't do anything, override this!'''
    def stop_draw(self) -> None:
        '''Updates the to_send list, removes it if it doesn't already exist in draw list'''
        if self.to_send in drawn_list:
            drawn_list.remove(self.to_send)
        self.to_send = (self.entities, self.pos, self.priority)
    def draw(self) -> None:
        '''Adds the entity to the draw list'''
        self.stop_draw()
        drawn_list.append(self.to_send)
    def update_priority(self, priority):
        '''Changes priority but text needs to be redrawn'''
        self.priority = priority

class Text(DrawnEntity):
    '''This class is for text on screen'''
    @override
    def __init__(self, text:str, pos:tuple[int,int], priority:int, font_size = 30,
                  text_color = (255, 255, 255), bg_color = (100, 100, 100)) -> None:
        self.text = text
        self.font_size = font_size
        self.text_color = text_color
        self.bg_color = bg_color
        super().__init__(priority, pos)
    @override
    def setup(self):
        self.current_text = self.get_text()
        self.entities.append(self.current_text)
    def get_text(self) -> pygame.Surface:
        '''Returns the text object from the data in the class'''
        return pygame.font.Font(size=self.font_size).render(
            self.text, True, self.text_color, self.bg_color)
    def update_text(self, text):
        '''Updates text without stopping'''
        self.text = text
        new_text = self.get_text()
        self.entities[self.entities.index(self.current_text)] = new_text
        self.current_text = new_text
    def update_and_stop_text(self, text):
        '''Stops text if it's running, and updates text'''
        self.update_text(text)
        self.stop_draw()
    def update_and_draw_text(self, text):
        '''Draws text while updating it'''
        self.update_text(text)
        self.draw()

class Sprite(DrawnEntity):
    '''Class with sprites'''
    def __init__(self, priority, pos, image_name) -> None:
        self.image = images_dict.get(image_name)
        if self.image is None:
            _logger.fatal("Texture %s not found!\nExiting...", image_name)
            Flags.running = False
            self.image = pygame.Surface(size=(100, 100))
            self.image.fill((100, 100, 100))
        super().__init__(priority, pos)
    def setup(self) -> None:
        self.entities.append(self.image)

class Note(Sprite):
    '''Class for not long notes'''
    def __init__(self, key:int) -> None:
        '''Pos is the key needed'''
        self.pos = [360+200*key,0]
        self.key = key
        super().__init__(-8, self.pos, "note")
        self.draw()
        note_list[key-1].append(self)
        self.tick_needed = TIME_NEEDED + Counters.ticks
        print(TIME_NEEDED, self.tick_needed)

    def move(self) -> None:
        '''Function that moves the note'''
        self.pos[1] += SCROLL_SPEED
        #Missed note
        if self.pos[1] > 1200:
            self.destroy()

    def judge(self) -> int:
        '''
        Note judgment\n
        Returns judgement score, if the judgement is not in range, return -1\n
        If it is in range, destroy the note
        '''
        #Excellent
        if self._within_range(EXCELLENT_RANGE):
            self.destroy()
            return 300
        if self._within_range(GOOD_RANGE):
            self.destroy()
            return 200
        if self._within_range(OK_RANGE):
            self.destroy()
            return 100
        if self._within_range(BAD_RANGE):
            self.destroy()
            return 50
        if self._within_range(MISS_RANGE):
            return 0
        return -1

    def _within_range(self, range:int) -> bool:
        if self.tick_needed-range <= self.tick_needed <= self.tick_needed+range:
            return True
        return False

    def destroy(self):
        '''Removes itself from note and draw list'''
        note_list[self.key-1].remove(self)
        drawn_list.remove(self.to_send)

class Wait():
    '''Class that is used to run code in delta ticks'''
    def __init__(self, delta, func:Callable, repeats=False) -> None:
        self.repeats = repeats
        self.needed_time = Counters.ticks + delta*TPS_CAP
        print(f"needed time {self.needed_time}")
        self.func = func
        if repeats:
            self.delta = delta
        delta_time_list.append(self)
    def is_true(self):
        if Counters.ticks < self.needed_time:
            return False
        else:
            return True
    def run(self):
        '''Runs the function, repeats if its on repeat'''
        print(f"needed tick {self.needed_time} current tick {Counters.ticks}")
        self.func()
        if self.repeats:
            self.needed_time+=self.delta*TPS_CAP
        else:
            delta_time_list.remove(self)
            del(self)
