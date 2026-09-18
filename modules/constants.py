'''Contains constants used by the game.'''

import enum

#Overall game
FPS_CAP = 60
HORIZONTAL_SIZE = 1920
VERTICAL_SIZE = 1080

#Gameplay
SCROLL_SPEED = 10
JUDGEMENT_LINE_HEIGHT = 60

IMAGE_FILE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

class ScreenEnum(enum.Enum):
    '''Contains the names of the screens in the game'''
    GAMEPLAY = enum.auto()
    MAIN_MENU = enum.auto()