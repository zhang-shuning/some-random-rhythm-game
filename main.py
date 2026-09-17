import pygame

from modules.classes import *
from modules.constants import *
from modules.shared_variables import *

#Pygame variable initialization
running:bool = True
screen = pygame.display.set_mode((HORIZONTAL_SIZE, VERTICAL_SIZE))
clock:pygame.time.Clock = pygame.time.Clock()
pygame.init()

Rect_Button("Hello world!", (100, 100), 1).draw()

while running:
    clock.tick(FPS_CAP)
    drawn_list.sort(key=lambda x:x[2])
    for i in drawn_list:
        for surface in i[0]:
            screen.blit(surface,i[1])
    pygame.display.flip()