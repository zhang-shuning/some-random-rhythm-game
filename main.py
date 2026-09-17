import pygame
import time

from modules.classes import *
from modules.constants import *
from modules.shared_variables import *

#Pygame variable initialization
running:bool = True
screen = pygame.display.set_mode((HORIZONTAL_SIZE, VERTICAL_SIZE))
clock:pygame.time.Clock = pygame.time.Clock()
pygame.init()

Text("Hello world!", (100, 100), 1).draw()
fps_text = Text("This should only show up on the first frame", (0, 0), 100)

while running:
    #Update clock
    cur_time = time.time()
    #Get events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    #Clear screen
    screen.fill((0,0,0))
    #Draw screen
    fps_text.update_and_draw_text(f"{clock.get_fps()}")
    drawn_list.sort(key=lambda x:x[2])
    for i in drawn_list:
        for surface in i[0]:
            screen.blit(surface,i[1])
    #Next frame
    pygame.display.flip()
    clock.tick(FPS_CAP)