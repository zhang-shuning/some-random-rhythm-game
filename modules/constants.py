'''Contains constants used by the game.'''

import enum

#Overall game
TPS_CAP = 180 #Input ticks
FPS_CAP = 60 #Display refreshes
FRAME_FREQUENCY = TPS_CAP//FPS_CAP #Assumes TPS and FPS are divisible
HORIZONTAL_SIZE = 1920
VERTICAL_SIZE = 1080
DEBUG = True

#Gameplay
SCROLL_SPEED = 10
JUDGEMENT_LINE_HEIGHT = 60
TIME_NEEDED = FRAME_FREQUENCY*(VERTICAL_SIZE-JUDGEMENT_LINE_HEIGHT)/(SCROLL_SPEED)

#Judgement
EXCELLENT = 64
GOOD = 97
OK = 127
BAD = 151
MISS = 188

IMAGE_FILE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

class ScreenEnum(enum.Enum):
    '''Contains the names of the screens in the game'''
    GAMEPLAY = enum.auto()
    MAIN_MENU = enum.auto()