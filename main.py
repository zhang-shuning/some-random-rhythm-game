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
fps_text = Text("0", (0, 0), 100)
def fps_wrapper(): fps_text.update_and_draw_text(str(clock.get_fps()))
fps_text.draw()
fps_update = Wait(1, fps_wrapper, True)

while running:
    #Update clock
    cur_time = time.time()
    #Get events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    #Get delta time events
    for i in delta_time_list:
        if i.is_true:
            i.run()
    #Clear screen
    screen.fill((0,0,0))
    #Draw screen
    drawn_list.sort(key=lambda x:x[2])
    for i in drawn_list:
        for surface in i[0]:
            screen.blit(surface,i[1])
    #Next frame
    pygame.display.flip()
    clock.tick(FPS_CAP)
