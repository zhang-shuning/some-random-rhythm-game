'''This file contains the classes used in the game!'''

from typing import Any, override
from collections.abc import Callable
import logging
import pygame

from modules.shared_variables import delta_time_list, Flags, Counters, drawn_list, images_dict
from modules.constants import *

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

class DrawnEntity():
    '''This is the base class for all entities that get drawn on screen.'''
    def __init__(self, priority:int, pos:tuple[int,int], origin = (0,0), center=False) -> None:
        self.pos = pos
        self.priority = priority
        self.entities = [] # Ordered so first thing appended is first
        self.to_send = ([], 0)
        self.is_drawn = False
        self.origin = origin
        if center:
            self.origin = (.5,.5)
        self.setup()

    def setup(self, entity_index=0) -> None:
        '''
        Where the entities get appended to the entitylist.\n
        Meant to be overridden.
        '''
        self.change_pos(self.entities[entity_index])

    def stop_draw(self) -> None:
        '''Updates the to_send list, removes it if it doesn't already exist in draw list'''
        if self.to_send in drawn_list:
            drawn_list.remove(self.to_send)
        self.to_send = [self.entities, self.pos, self.priority]
        self.is_drawn = False

    def draw(self) -> None:
        '''Adds the entity to the draw list'''
        self.stop_draw()
        drawn_list.append(self.to_send)
        self.is_drawn = True

    def update_priority(self, priority):
        '''Changes priority but text needs to be redrawn'''
        self.priority = priority

    def change_pos(self, surface):
        if self.origin != (0,0):
            x = round(self.pos[0] - surface.get_width() * self.origin[0])
            y = round(self.pos[1] - surface.get_height() * self.origin[1])
            self.pos = (x,y)
            print(self.pos)


class Text(DrawnEntity):
    '''This class is for text on screen'''
    def __init__(self, text:str, pos:tuple[int,int], priority:int, font_size:int = 30, origin = (0,0),
                  text_color:tuple[int,int,int] = (255, 255, 255), bg_color:tuple[int,int,int]|None = None) -> None:
        self.text = text
        self.font_size = font_size
        self.text_color = text_color
        self.bg_color = bg_color
        super().__init__(priority, pos, origin=origin)

    @override
    def setup(self, entity_index=0):
        self.current_text = self.get_text()
        self.entities.append(self.current_text)
        super().setup(entity_index=entity_index)

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
    def __init__(self, priority, pos, image_name, origin = (0,0)) -> None:
        self.image = images_dict.get(image_name)
        if self.image is None:
            _logger.fatal("Texture %s not found!\nExiting...", image_name)
            Flags.running = False
            self.image = pygame.Surface(size=(100, 100))
            self.image.fill((100, 100, 100))
        super().__init__(priority, pos, origin=origin)

    @override
    def setup(self) -> None:
        self.entities.append(self.image)

class Wait():
    '''Class that is used to run code in delta ticks'''
    def __init__(self, delta, func:Callable, *args, repeats=False) -> None:
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
        super().__init__(delta, func, *args, repeats=True)

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

class Button(Text):
    def __init__(self, text: str, pos: tuple[int, int], priority: int, font_size: int = 30,
                text_color: tuple[int, int, int] = (255, 255, 255), bg_color: tuple[int, int, int] | None = None,
                rect_color = (0,0,0), rect_size = (0, 0), rect_texture = None, on_press:Callable = lambda: None) -> None:
        super().__init__(text, pos, priority, font_size, text_color, bg_color)