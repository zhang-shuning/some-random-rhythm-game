'''Also text based for now.'''
from dataclasses import dataclass
from typing import TYPE_CHECKING
import hashlib
import pathlib
import struct

import pygame

from modules.classes import Scene, Text
from modules.scripts import handle_fblits
from modules.constants import *

if TYPE_CHECKING:
    from main import GameController

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
exit:  closes the program
back:  goes back to level selector
save:  save file

note: adds a note
args: time(float) pos(0-3)
ln: adds a long note
args: time start(float) time end(float) pos(0-3)
'''

@dataclass
class Map():
    song_name:str
    artist_name:str
    difficulty_name:str
    bpm:int
    saved:bool = False

def str_fits_in_u_short(n:str):
        if len(n.format("utf-8")) > 2**16-1:
            return True
        return False

class MapMakerScene(Scene):
    def __init__(self, game: GameController) -> None:
        super().__init__(game)
        self.current_map = None

        self.note_timing_list = [] # (LN/Normal, pos, time start, (time end))

    def run_command(self, command:str):
        global current_map
        args = command.split()
        if len(args) == 0:
            return
        cmd = args[0]
        if cmd == "exit":
            self.game.running = False
        elif cmd == "back":
            self.game.new_scene = True
            self.game.next_scene_str = "level_selector"
        elif cmd == "note":
            try:
                self.response.update_and_draw_text("Note added")
            except ValueError:
                self.response.update_and_draw_text("something went wrong with the command")
        elif cmd == 'ln':
            try:
                self.response.update_and_draw_text("Note added")
            except ValueError:
                self.response.update_and_draw_text("something went wrong with the command")
        elif cmd == 'save':
            self.note_timing_list.sort(key=lambda x:x[1])
        else:
            self.response.update_and_draw_text("")

    def handle_event(self,event:pygame.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if DEBUG:
                self.mouse_text.update_and_draw_text(f"{pygame.mouse.get_pos()}")
                print(f"mouse pos {pygame.mouse.get_pos()}")
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.running = False
            elif event.key == pygame.K_BACKSPACE and (event.mod & pygame.KMOD_CTRL):
                self.text_box.update_and_draw_text("")
            elif event.key == pygame.K_BACKSPACE:
                self.text_box.update_and_draw_text(self.text_box.text[:-1])
            elif event.key == pygame.K_RETURN:
                self.run_command(self.text_box.text)
                self.text_box.update_and_draw_text("")
        elif event.type == pygame.TEXTINPUT:
            self.text_box.update_and_draw_text(self.text_box.text + event.text)

    def render(self,screen):
        screen.fill((0,100,152))
        screen.fblits(handle_fblits(self.drawn_list))

    def scene_init(self):
        self.mouse_text = Text(self.game, "", (HORIZONTAL_SIZE-500,0), 100)
        self.intro_text = Text(self.game, intro_string, (0,0), 10, 30)
        self.text_box = Text(self.game, "", (700, 25), 10)
        self.response = Text(self.game, "", (0, 900), 10, font_size=60)
        self.intro_text.draw()

    def save_map(self):
            #Ensure all strings don't go over the max length for u16
            if not str_fits_in_u_short(Map.song_name):
                self.response.update_and_draw_text("The song name is too long (max 65535)")
                return
            if not str_fits_in_u_short(Map.artist_name):
                self.response.update_and_draw_text("The artist name is too long (max 65535)")
                return
            if not str_fits_in_u_short(Map.difficulty_name):
                self.response.update_and_draw_text("The difficulty name is too long (max 65535)")
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

            for i in self.note_timing_list:
                if i[0] == 1: # long note
                    byte_list += struct.pack(">b", 128 + i[1])
                    byte_list += struct.pack(">d", i[2])
                    byte_list += struct.pack(">d", i[3])
                else:
                    byte_list += struct.pack(">b", i[1])
                    byte_list += struct.pack(">d", i[2])
