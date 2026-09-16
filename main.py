import pygame
import modules.classes
import modules.scripts

from modules.constants import *
from modules.shared_variables import *

#Pygame variable initialization
running:bool = True
screen = pygame.display.set_mode((HORIZONTAL_SIZE, VERTICAL_SIZE))
clock:pygame.time.Clock = pygame.time.Clock()

while running:
    clock.tick(FPS_CAP)
    for i in rects_to_draw:
        pygame.draw.rect(screen, (255,255,255), i)
    pygame.display.flip()