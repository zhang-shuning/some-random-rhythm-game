'''This file includes functions that are important to make stuff appear on screen'''
import pygame
import pathlib
from modules.shared_variables import images_dict
from modules.constants import IMAGE_FILE_EXTENSIONS

def switch_screen(screen:int):
    '''Switch to screen in the input'''

def init_screens():
    '''Initializes the basic features for each screen'''

def _load_image(image_path:str|pathlib.Path, texture_name:str, transparent=False):
    '''Loads a single image and saves to dictionary based from filename'''
    if not transparent:
        images_dict[texture_name] = pygame.image.load(image_path)
    else:
        images_dict[texture_name] = pygame.image.load(image_path).convert_alpha()

def load_images():
    '''Loads all images and saves them to a dictionary'''
    print("Loading images...")
    assets_folder = pathlib.Path("assets/textures")
    for item in assets_folder.rglob("*"):
        if item.is_file() and item.suffix in IMAGE_FILE_EXTENSIONS:
            print(item.name)
            _load_image(item, item.stem)

if __name__ == "__main__":
    load_images()