'''This file contains the classes used in the game!'''

import pygame
from modules.shared_variables import *

class DrawnEntity():
    def __init__(self, priority, pos) -> None:
        self.pos = pos
        self.priority = priority
        self.entities = [] # Ordered so first thing appended is first
        self.to_send = ([], 0)
    def stop_draw(self) -> None:
        '''Updates the to_send list, removes it if it doesn't already exist in draw list'''
        if self.to_send in drawn_list:
            drawn_list.remove(self.to_send)
        self.to_send = (self.entities, self.pos, self.priority)
    def draw(self) -> None:
        '''Adds the entity to the draw list '''
        self.stop_draw()
        drawn_list.append(self.to_send)

class Rect_Button(DrawnEntity):
    def __init__(self, text:str, pos, priority, font_size = 30,
                  text_color = (255, 255, 255), rect_additional_size = 0, rectangle_color = (0, 0, 0)) -> None:
        super().__init__(priority, pos)
        self.font = pygame.font.Font(size=font_size).render(text, True, text_color, rectangle_color)
        self.font_rect = self.font.get_rect(center=pos)
        self.entities.append(self.font)
