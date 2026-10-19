from modules.classes import *
from modules.scripts import handle_fblits
from modules.shared_variables import fblits_list, Counters, Flags, StringFlags

pygame.font.init()

def goto_level_select():
    Flags.new_scene = True
    StringFlags.cur_scene = "level_selector"

def exit_game():
    Flags.running = False

background = Sprite(-1, (0,0), "title_image")
play_button = Button("Play Game", (1100,300), 10, rect_size=(500,100), rect_color=(100,100,0), on_press=goto_level_select)
settings_button = Button("Settings", (1100,550), 10, rect_size=(500,100))
exit_button = Button("Exit Game", (1100,800), 10, rect_size=(500,100), on_press=exit_game, rect_color=(0,100,100))

def init():
    background.draw()
    play_button.draw()
    settings_button.draw()
    exit_button.draw()

def event_handler(event:pygame.Event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            Flags.running = False

def render(screen):
    if Counters.ticks % FRAME_FREQUENCY == 0:
        screen.fill((152,100,0))
        handle_fblits()
        screen.fblits(fblits_list)
        pygame.display.flip()

scene = Scene("main_menu", event_handler, render=render, scene_init_function=init)
main_menu_elements = (play_button, settings_button, exit_button)

def open_main_menu():
    for element in main_menu_elements: 
        element.draw()

def close_main_menu():
    for element in main_menu_elements:
        element.stop_draw()
