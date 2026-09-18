'''Contains constants used by the game.'''

import enum

#Overall game
FPS_CAP = 60
HORIZONTAL_SIZE = 1920
VERTICAL_SIZE = 1080

#Gameplay
SCREEN_RATIO = HORIZONTAL_SIZE/VERTICAL_SIZE
BOX_SIZE = (HORIZONTAL_SIZE//2, VERTICAL_SIZE)


IMAGE_FILE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

class ScreenEnum(enum.Enum):
    '''Enum to store the names of the screens'''
    GAMEPLAY = enum.auto()
    MAIN_MENU = enum.auto()