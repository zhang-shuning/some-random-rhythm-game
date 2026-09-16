import pygame
import modules.classes
import modules.scripts

FPS_CAP = 60
HORIZONTAL_SIZE = 800
VERTICAL_SIZE = 600

#Pygame variable initialization
running:bool = True
screen = pygame.display.set_mode((HORIZONTAL_SIZE, VERTICAL_SIZE))
clock:pygame.time.Clock = pygame.time.Clock()
rects_to_draw:list[pygame.Rect] = [
    pygame.Rect(100,100,100,100)
]

while running:
    clock.tick(FPS_CAP)
    for i in rects_to_draw:
        pygame.draw.rect(screen, (255,255,255), i)
    pygame.display.flip()