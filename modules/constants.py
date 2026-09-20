'''Contains constants used by the game.'''

import enum

def _round_to_nearest_odd(n):
    '''AI function because I can't be bothered to think'''
    return round((n - 1) / 2) * 2 + 1

def _get_odd_ticks_from_ms(n):
    return _round_to_nearest_odd(n*TPS_CAP/1000)

def _get_range(n):
    return n//2

#Overall game
TPS_CAP = 60 #Input ticks
FPS_CAP = 60 #Display refreshes
FRAME_FREQUENCY = TPS_CAP//FPS_CAP #Assumes TPS and FPS are divisible
MS_PER_TICK = 1/TPS_CAP*1000
HORIZONTAL_SIZE = 1920
VERTICAL_SIZE = 1080
DEBUG = True

#Text pos
JUDEMENT_TEXT_POS = (960, 250)

#Gameplay
SCROLL_SPEED = 15*60/FPS_CAP
HITLIGHT_DISABLE_TIME = .05
JUDGEMENT_LINE_HEIGHT = 60
TIME_NEEDED = FRAME_FREQUENCY*(VERTICAL_SIZE-JUDGEMENT_LINE_HEIGHT)/(SCROLL_SPEED)

#Judgement
MAXMUM_JUDGEMENT_TEXT_FRAMES = 30
MINIMUM_JUDGEMENT_TEXT_FRAMES = 1

EXCELLENT_MS = 64
GOOD_MS = 97
OK_MS = 127
BAD_MS = 151
MISS_MS = 188

EXCELLENT_TICKS = _get_odd_ticks_from_ms(EXCELLENT_MS)
GOOD_TICKS = _get_odd_ticks_from_ms(GOOD_MS)
OK_TICKS = _get_odd_ticks_from_ms(OK_MS)
BAD_TICKS = _get_odd_ticks_from_ms(BAD_MS)
MISS_TICKS = _get_odd_ticks_from_ms(MISS_MS)

EXCELLENT_RANGE = _get_range(EXCELLENT_TICKS)
GOOD_RANGE = _get_range(GOOD_TICKS)
OK_RANGE = _get_range(OK_TICKS)
BAD_RANGE = _get_range(BAD_TICKS)
MISS_RANGE = _get_range(MISS_TICKS)


IMAGE_FILE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

class ScreenEnum(enum.Enum):
    '''Contains the names of the screens in the game'''
    GAMEPLAY = enum.auto()
    MAIN_MENU = enum.auto()

if __name__ == "__main__":
    print(EXCELLENT_TICKS)
    print(GOOD_TICKS)
    print(OK_TICKS)
    print(BAD_TICKS)  
    print(MISS_TICKS)
