import pygame
import time

from modules.classes import *
from modules.constants import *
from modules.shared_variables import *
from modules.scripts import *

#Pygame variable initialization
running:bool = True
screen = pygame.display.set_mode((HORIZONTAL_SIZE, VERTICAL_SIZE),pygame.FULLSCREEN | pygame.SCALED)
clock:pygame.time.Clock = pygame.time.Clock()
pygame.init()
load_images()

Sprite(-1, (HORIZONTAL_SIZE/4, 0), "test").draw()

Text("Hello world!", (100, 100), .2).draw()
mouse_text = Text("", (HORIZONTAL_SIZE-200,0), 100)
fps_text = Text("0", (0, 0), 100)
def fps_wrapper(): fps_text.update_and_draw_text(str(clock.get_fps()))
fps_text.draw()
fps_update = Wait(1, fps_wrapper, True)

while running:
    print(clock.get_fps())
    #Update clock
    cur_time = time.time()
    #Get events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_text.update_and_draw_text(f"{pygame.mouse.get_pos()}")
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
    handle_fblits()
    screen.fblits(fblits_list)
    #Next frame
    pygame.display.flip()
    clock.tick(FPS_CAP)
