'''This file includes functions that are important to make stuff appear on screen'''
import pygame
import pathlib

from modules.shared_variables import *
from modules.constants import IMAGE_FILE_EXTENSIONS, HORIZONTAL_SIZE, VERTICAL_SIZE, ScreenEnum
from modules.classes import Sprite

def switch_screen(screen:int):
    '''Switch to screen in the input'''

def init_screens():
    '''Initializes the basic features for each screen'''

def reset_game_screen():
    '''Resets the game scene'''
    Sprite(-1, (HORIZONTAL_SIZE/4, 0), "test").draw()

def _load_image(image_path:str|pathlib.Path, texture_name:str, transparent=False):
    '''Loads a single image and saves to dictionary based from filename'''
    if not transparent:
        images_dict[texture_name] = pygame.image.load(image_path).convert()
    else:
        images_dict[texture_name] = pygame.image.load(image_path).convert_alpha()

def load_images() -> None:
    '''Loads all images and saves them to a dictionary'''
    print("Loading images...")
    assets_folder = pathlib.Path("assets/textures")
    for item in assets_folder.rglob("*"):
        if item.is_file() and item.suffix in IMAGE_FILE_EXTENSIONS:
            print(item.name)
            _load_image(item, item.stem)

def handle_fblits():
    '''Updates fblits list from the drawn list'''
    drawn_list.sort(key=lambda x:x[2])
    fblits_list.clear()
    for i in drawn_list:
        for surface in i[0]:
            fblits_list.append((surface, i[1]))

if __name__ == "__main__":
    load_images()