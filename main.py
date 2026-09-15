import pygame

FPS_CAP = 60

#Pygame variable initialization
running:bool = True
clock:pygame.time.Clock = pygame.time.Clock()

while running:
    clock.tick(FPS_CAP)