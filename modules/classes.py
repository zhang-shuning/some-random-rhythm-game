'''This file contains the classes used in the game!'''
# pylint: disable=function-redefined
from typing import Any, override
from collections.abc import Callable
from abc import ABC, abstractmethod
import logging
from typing import TYPE_CHECKING

import pygame

from modules.constants import *

if TYPE_CHECKING:
    from main import GameController
    from pygame import Rect

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

class AbstractDrawable(ABC):
    '''Abstract class defining drawable classes'''
    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def stop_draw(self):
        pass

class DrawnEntity(AbstractDrawable):
    '''This is the base class for all entities that get drawn on screen.'''
    def __init__(self, game:GameController, priority:int, pos:tuple[int,int]|list[int], origin = (0,0), center=False, is_global=False) -> None:
        '''If scene is none, then it it is global'''
        self.orig_pos = pos
        self.pos = pos
        self.priority = priority
        self.entities = [] # Ordered so first thing appended is first
        self.to_send = ([], 0, 0)
        self.is_drawn = False
        self.origin = origin
        if center:
            self.origin = (.5,.5)
        if is_global:
            self.drawn_list = game.global_draw_list
        else:
            self.drawn_list = game.cur_scene.drawn_list
        self.setup()

    def setup(self, entity_index=0) -> None:
        '''
        Where the entities get appended to the entitylist.\n
        Meant to be overridden.
        '''
        self.change_pos(self.entities[entity_index])

    @override
    def stop_draw(self) -> None:
        '''Updates the to_send list, removes it if it doesn't already exist in draw list'''
        if self.to_send in self.drawn_list:
            self.drawn_list.remove(self.to_send)
        self.to_send = [self.entities, self.pos, self.priority]
        self.is_drawn = False

    @override
    def draw(self) -> None:
        '''Adds the entity to the draw list'''
        self.stop_draw()
        self.drawn_list.append(self.to_send)
        self.is_drawn = True

    def update_priority(self, priority):
        '''Changes priority but text needs to be redrawn'''
        self.priority = priority

    def change_pos(self, surface):
        if self.origin != (0,0):
            x = int(self.orig_pos[0] - surface.get_width() * self.origin[0])
            y = int(self.orig_pos[1] - surface.get_height() * self.origin[1])
            #print(f"origin {self.origin} old pos {self.orig_pos} new pos {(x,y)}")
            self.pos = (x,y)

class DrawbleRect(AbstractDrawable):
    '''No origin because I don't feel like it'''
    def __init__(self, game, priority, pos, size:tuple[int,int]|list[int], color, scene:Scene|None = None) -> None:
        self.pos=pos
        self.priority=priority
        self.rect = pygame.surface.Surface(size=size)
        self.rect.fill(color=color)
        self.to_send = [[self.rect], pos, priority]
        if scene is None:
            self.drawn_list = game.global_draw_list
        else:
            self.drawn_list = scene.drawn_list

    @override
    def stop_draw(self) -> None:
        '''Updates the to_send list, removes it if it doesn't already exist in draw list'''
        if self.to_send in self.drawn_list:
            self.drawn_list.remove(self.to_send)
        self.to_send = [[self.rect], self.pos, self.priority]

    @override
    def draw(self) -> None:
        '''Adds the entity to the draw list'''
        self.stop_draw()
        self.drawn_list.append(self.to_send)

class Text(DrawnEntity):
    '''This class is for text on screen'''
    def __init__(self, game:GameController, text:str, pos:tuple[int,int], priority:int, font_size:int = 30, origin = (0,0),
                text_color:tuple[int,int,int] = (255, 255, 255),
                bg_color:tuple[int,int,int]|None = None, is_global:bool = False) -> None:
        self.text = text
        self.font_size = font_size
        self.text_color = text_color
        self.bg_color = bg_color
        super().__init__(game, priority, pos, origin=origin, is_global=is_global)

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
        super().setup(entity_index=0)

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
    def __init__(self, game, priority, pos, image_name, origin = (0,0)) -> None:
        self.image = game.images_dict.get(image_name)
        if self.image is None:
            _logger.fatal("Texture %s not found!\nExiting...", image_name)
            game.running = False
            self.image = pygame.Surface(size=(100, 100))
            self.image.fill((100, 100, 100))
        super().__init__(game, priority, pos, origin=origin)

    @override
    def setup(self, entity_index=0) -> None:
        self.entities.append(self.image)

class Wait():
    '''Class that is used to run code in delta ticks'''
    def __init__(self, game:GameController, delta, func:Callable, *args,
                repeats=False, is_global = False) -> None:
        '''
        If scene is None, then it uses the global delta time list
        Otherwise, use the scene ticks
        '''

        if not is_global:
            scene = game.cur_scene
            self.tick = lambda:scene.scene_ticks
            self.delta_list = scene.delta_time_list
        else:
            self.tick = lambda:game.ticks
            self.delta_list = game.global_delta_time_list
        self.repeats = repeats
        self.needed_time = self.tick() + delta*TPS_CAP
        self.func = func
        self.args = args
        if repeats:
            self.delta = delta

    def time_passed(self):
        '''Returns whether the time passed yet or not'''
        if self.tick() < self.needed_time:
            return False
        else:
            return True

    def run(self):
        '''Runs the function, repeats if its on repeat'''
        self.func(*self.args)
        if self.repeats:
            self.needed_time+=self.delta*TPS_CAP
        else:
            self.delta_list.remove(self)
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
            self.needed_time = self.delta*TPS_CAP + self.tick()
        else:
            self.needed_time = time*TPS_CAP + self.tick()

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
    '''The function runs when the user clicks on the button.'''
    def __init__(self, game:GameController, text: str, pos: tuple[int, int], priority: int, font_size: int = 30, origin = (0,0),
                text_color: tuple[int, int, int] = (255, 255, 255), bg_color: tuple[int, int, int] | None = None,
                rect_color = (0,0,0), rect_size = (0, 0), rect_texture = None, on_press:Callable = lambda: None, ) -> None:
        #Rect is a seperate rect around the text
        self.rect_color = rect_color
        self.rect_size = rect_size
        self.on_press = on_press
        self.cur_rect_and_func = None
        self.rect_list = game.button_list
        super().__init__(game, text, pos, priority, font_size, origin, text_color, bg_color)
    def update_rect(self):
        if self.cur_rect_and_func in self.rect_list:
           self.rect_list.remove(self.cur_rect_and_func)
        self.cur_rect_and_func = (pygame.Rect(self.pos, self.rect_size), self.on_press)
        self.rect_list.append(self.cur_rect_and_func)
    @override
    def setup(self, entity_index=0):
        surface = pygame.Surface(size=self.rect_size)
        surface.fill(self.rect_color)
        self.entities.append(surface)
        super().setup(entity_index)
    @override
    def draw(self) -> None:
        super().draw()
        self.update_rect()
    @override
    def stop_draw(self) -> None:
        if self.cur_rect_and_func in self.rect_list:
            self.rect_list.remove(self.cur_rect_and_func)
        return super().stop_draw()

class Scene():
    '''
    The base class for all scenes\n
    In chronological order the methods are run in:\n
    handle_event(event) is the event handler\n
    handle_held_keys(keys) is the held key handler\n
    pre_render()/render()/after_render() is meant for rendering
    tick() increases the tick count
    '''
    def __init__(self, game:GameController) -> None:

        self.game = game
        self.scene_ticks = 0

        #Setup/internal buffers
        self.surface_dict = {} #The surface dict will store drawn lists
        self.drawn_list = [] # [[surface, pos, priority]]
        self.fblits_list = [] # list for fblits
        self.destroy_list = [] # List of object to be destroyed at end of frame
        self.rect_list:list[tuple[Rect, Callable[[]]]] = [] #List of buttons
        self.delta_time_list:list[Wait] = [] #List of delta time objects

    def scene_init(self):
        pass

    def handle_event(self, event):
        pass

    def handle_held_keys(self, keys):
        pass

    def pre_render(self):
        pass

    def render(self, screen):
        pass

    def after_render(self):
        pass

    def tick(self):
        self.scene_ticks += 1

class PausableScene(Scene):
    '''Class for scenes that are pausable (likely just replay and gameplay for now)'''
    def __init__(self, game:GameController) -> None:
        self.unpaused_ticks = 0
        self.is_paused = False
        super().__init__(game)
