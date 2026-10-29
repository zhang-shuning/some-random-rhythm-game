'''This file includes functions that are important to make stuff appear on screen'''
import pygame
import pathlib
from typing import TYPE_CHECKING

from modules.shared_variables import *
from modules.constants import IMAGE_FILE_EXTENSIONS, HORIZONTAL_SIZE

if TYPE_CHECKING:
    from main import GameController

def switch_screen(screen:int):
    '''Switch to screen in the input'''

def init_screens():
    '''Initializes the basic features for each screen'''

def reset_game_screen():
    '''Resets the game scene'''
    print("test")

def _load_image(game:GameController, image_path:str|pathlib.Path, texture_name:str, transparent=False):
    '''Loads a single image and saves to dictionary based from filename'''
    if not transparent:
        game.images_dict[texture_name] = pygame.image.load(image_path).convert()
    else:
        game.images_dict[texture_name] = pygame.image.load(image_path).convert_alpha()

def load_images(game:GameController) -> None:
    '''Loads all images and saves them to a dictionary'''
    print("Loading images...")
    textures_folder = pathlib.Path("assets/textures")
    transparent_texture_folder = pathlib.Path("assets/textures-transparent")

    for item in textures_folder.rglob("*"):
        if item.is_file() and item.suffix in IMAGE_FILE_EXTENSIONS:
            print(item.name)
            _load_image(game, item, item.stem)
    
    for item in transparent_texture_folder.rglob("*"):
        if item.is_file() and item.suffix in IMAGE_FILE_EXTENSIONS:
            print(item.name)
            _load_image(game, item, item.stem, transparent=True)

def handle_fblits(drawn_list[list]):
    '''Updates fblits list from the drawn list'''
    drawn_list.sort(key=lambda x:x[2])
    fblits_list = []
    for i in drawn_list:
        for surface in i[0]:
            fblits_list.append((surface, i[1]))
    return fblits_list

#if __name__ == "__main__":
    #load_images()
