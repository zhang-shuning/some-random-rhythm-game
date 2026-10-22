'''Also text based for now.'''
from dataclasses import dataclass
import hashlib
import pathlib
import struct

import pygame

from modules.classes import Scene, Text
from modules.scripts import handle_fblits
from modules.shared_variables import *
from modules.constants import *

'''
The plan for the map is to have the file store the timings of the notes, and convert it to ticks when reading the note
The header should include version, song, artist, difficulty name, bpm, with the id being a combination of the 3 in the DB
Header format:
File format ID, version, (song name bytes), song name, (artist name bytes), artist name, (difficulty name bytes) difficulty name,
checksum (song name, artist name, difficulty name hashed together), then data
The data should be stored as note/LN and pos in 1 byte, then the float for time start (and then time end if LN)
'''

intro_string = '''
This is a (hopefully) temporary text based console.
So far:
exit closes the program
back goes back to main menu
note time (float) pos(0-3)
ln time start (float) time end (float) pos(0-3)
'''

intro_text = Text(intro_string, (0,0), 10, 30)
text_box = Text("", (0, 200), 10)
response = Text("", (0, 900), 10)

@dataclass
class Map():
    song_name:str
    artist_name:str
    difficulty_name:str
    bpm:int
    saved:bool = False

current_map = None

note_timing_list = [] # (LN/Normal, pos, time start, (time end))

def run_command(command:str):
    global current_map
    args = command.split()
    if len(args) == 0:
        return
    cmd = args[0]
    if cmd == "exit":
        Flags.running = False
    elif cmd == "back":
        Flags.new_scene = True
        StringFlags.cur_scene = "main_menu"
    elif cmd == "note":
        try:
            pass
        except ValueError:
            response.update_and_draw_text("something went wrong with the command")
    elif cmd == 'ln':
        try:
            pass
        except ValueError:
            response.update_and_draw_text("something went wrong with the command")
    elif cmd == 'save':
        note_timing_list.sort(key=lambda x:x[1])
    elif cmd == 'exit':


def event_handler(event:pygame.Event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            Flags.running = False
        elif event.key == pygame.K_BACKSPACE and (event.mod & pygame.KMOD_CTRL):
            text_box.update_and_draw_text("")
        elif event.key == pygame.K_BACKSPACE:
            text_box.update_and_draw_text(text_box.text[:-1])
        elif event.key == pygame.K_RETURN:
            run_command(text_box.text)
            text_box.update_and_draw_text("")
    elif event.type == pygame.TEXTINPUT:
        text_box.update_and_draw_text(text_box.text + event.text)

def render(screen):
    if Counters.ticks % FRAME_FREQUENCY == 0:
        screen.fill((152,100,0))
        handle_fblits()
        screen.fblits(fblits_list)
        pygame.display.flip()

def scene_init():
    intro_text.draw()

def make_scene():
    Scene("map_maker", event_handler=event_handler,
            render=render, scene_init_function=scene_init)

def str_fits_in_u_short(n:str):
    if len(n.format("utf-8")) > 2**16-1:
        return True
    return False

def save_map():
    #Ensure all strings don't go over the max length for u16
    if not str_fits_in_u_short(Map.song_name):
        response.update_and_draw_text("The song name is too long (max 65535)")
        return
    if not str_fits_in_u_short(Map.artist_name):
        response.update_and_draw_text("The artist name is too long (max 65535)")
        return
    if not str_fits_in_u_short(Map.difficulty_name):
        response.update_and_draw_text("The difficulty name is too long (max 65535)")
        return
    
    pathlib.Path("maps").mkdir(exist_ok=True)
    file_name = f"{Map.artist_name} - {Map.song_name} ({Map.difficulty_name}).rgmap"
    file_path = pathlib.Path("maps") / file_name
    byte_list = bytearray(b"RGMap\032\n")

    #Version number
    byte_list += struct.pack(">b", 1)

    #Lengths for strings
    byte_list += struct.pack(">h", len(Map.song_name.encode("utf-8")))
    byte_list += struct.pack(">h", len(Map.artist_name.encode("utf-8")))
    byte_list += struct.pack(">h", len(Map.difficulty_name.encode("utf-8")))

    #Strings
    byte_list += Map.song_name.encode("utf-8")
    byte_list += Map.artist_name.encode("utf-8")
    byte_list += Map.difficulty_name.encode("utf-8")

    #Adds a checksum
    byte_list += hashlib.md5((Map.artist_name+Map.song_name+Map.difficulty_name).encode("utf-8")).digest()

    for i in note_timing_list:
        if i[0] == 1: # long note
            byte_list += struct.pack(">b", 128 + i[1])
            byte_list += struct.pack(">d", i[2])
            byte_list += struct.pack(">d", i[3])
        else:
            byte_list += struct.pack(">b", i[1])
            byte_list += struct.pack(">d", i[2])
