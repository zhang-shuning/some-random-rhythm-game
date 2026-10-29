'''This file includes functions that are important to make stuff appear on screen'''
import pygame
import pathlib
from typing import TYPE_CHECKING

from modules.constants import IMAGE_FILE_EXTENSIONS

if TYPE_CHECKING:
    from main import GameController

def handle_fblits(drawn_list:list):
    '''Updates fblits list from the drawn list'''
    drawn_list.sort(key=lambda x:x[2])
    print(drawn_list)
    fblits_list = []
    for i in drawn_list:
        for surface in i[0]:
            fblits_list.append((surface, i[1]))
    return fblits_list

#if __name__ == "__main__":
    #load_images()
