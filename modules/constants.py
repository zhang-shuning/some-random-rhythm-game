'''Contains constants used by the game.'''

import enum

FPS_CAP = 60
HORIZONTAL_SIZE = 800
VERTICAL_SIZE = 600

class ScreenEnum(enum.Enum):
    '''Enum to store the names of the screens'''
    GAMEPLAY = enum.auto()
    MAIN_MENU = enum.auto()