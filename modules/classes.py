'''This file contains the classes used in the game!'''

from typing import Any, override
from collections.abc import Callable
import logging
import pygame

from modules.shared_variables import delta_time_list, Flags, Counters, drawn_list, images_dict, note_list
from modules.constants import *

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

class DrawnEntity():
    '''This is the base class for all entities that get drawn on screen.'''
    def __init__(self, priority:int, pos:tuple[int,int]) -> None:
        self.pos = pos
        self.priority = priority
        self.entities = [] # Ordered so first thing appended is first
        self.to_send = ([], 0)
        self.is_drawn = False
        self.setup()

    def setup(self) -> None:
        '''
        Where the entities get appended to the entitylist.\n
        Meant to be overridden.
        '''

    def stop_draw(self, center_pos = False, entity_index=0) -> None:
        '''Updates the to_send list, removes it if it doesn't already exist in draw list'''
        if self.to_send in drawn_list:
            drawn_list.remove(self.to_send)
        if center_pos:
            self.to_send = [self.entities, self.center_pos(self.entities[entity_index]), self.priority]
        else:
            self.to_send = [self.entities, self.pos, self.priority]
        self.is_drawn = False

    def draw(self, center_pos = False, entity_index=0) -> None:
        '''Adds the entity to the draw list'''
        self.stop_draw(center_pos, entity_index)
        drawn_list.append(self.to_send)
        self.is_drawn = True

    def update_priority(self, priority):
        '''Changes priority but text needs to be redrawn'''
        self.priority = priority

    def center_pos(self, surface:pygame.Surface) -> tuple[int,int]:
        '''Returns pos to centered coordinates from surface and coordinates'''
        x = self.pos[0] - surface.get_width() // 2
        y = self.pos[1] - surface.get_height() // 2
        return (x, y)


class Text(DrawnEntity):
    '''This class is for text on screen'''
    def __init__(self, text:str, pos:tuple[int,int], priority:int, font_size:int = 30,
                  text_color:tuple[int,int,int] = (255, 255, 255), bg_color:tuple[int,int,int]|None = None) -> None:
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
        if self.bg_color:
            return pygame.font.Font(size=self.font_size).render(
                self.text, True, self.text_color, self.bg_color)
        #Transparent
        return pygame.font.Font(size=self.font_size).render(
            self.text, True, self.text_color)

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

    @override
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

    def move(self) -> None:
        '''Function that moves the note'''
        self.pos[1] += SCROLL_SPEED
        #Missed note
        if self.pos[1] > VERTICAL_SIZE:
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
        if self.tick_needed-range <= Counters.ticks <= self.tick_needed+range:
            return True
        return False

    def destroy(self):
        '''Removes itself from note and draw list'''
        note_list[self.key-1].remove(self)
        drawn_list.remove(self.to_send)

class Wait():
    '''Class that is used to run code in delta ticks'''
    def __init__(self, delta, func:Callable, repeats=False, *args) -> None:
        self.repeats = repeats
        self.needed_time = Counters.ticks + delta*TPS_CAP
        self.func = func
        self.args = args
        if repeats:
            self.delta = delta
        delta_time_list.append(self)

    def time_passed(self):
        '''Returns whether the time passed yet or not'''
        if Counters.ticks < self.needed_time:
            return False
        else:
            return True

    def run(self):
        '''Runs the function, repeats if its on repeat'''
        self.func(*self.args)
        if self.repeats:
            self.needed_time+=self.delta*TPS_CAP
        else:
            delta_time_list.remove(self)
            del(self)

class WaitExtendable(Wait):
    '''Wait class but the time when the function happens can be extended'''
    def __init__(self, delta, func: Callable[..., Any], *args) -> None:
        self.activated = False
        super().__init__(delta, func, True, *args)

    def set_time(self, time:int|float=-1):
        '''
        Sets timer to time seconds\n
        If it is negative, then use the default
        '''
        self.activated = True
        if time < 0:
            self.needed_time = self.delta*TPS_CAP + Counters.ticks
        else:
            self.needed_time = time*TPS_CAP + Counters.ticks

    @override
    def time_passed(self):
        if self.activated:
            return super().time_passed()
        return False
    @override
    def run(self):
        self.activated = False
        self.func()
        
