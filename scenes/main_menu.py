from modules.classes import *

pygame.font.init()
play_button = Button("Play Game", (100,100), 10, rect_color=(255,255,255))
settings_button = Button("Settings", (200,100), 10, rect_color=(255,255,255))
exit_button = Button("Exit Game", (100,200), 10, rect_color=(255,255,255))

main_menu_elements = (play_button, settings_button, exit_button)

def open_main_menu():
    for element in main_menu_elements: 
        element.draw()

def close_main_menu():
    for element in main_menu_elements:
        element.draw()

if __name__ == "__main__":
    from modules.scripts import *
    open_main_menu()
    clock = pygame.Clock()
    screen = pygame.display.set_mode((HORIZONTAL_SIZE, VERTICAL_SIZE),pygame.FULLSCREEN | pygame.SCALED)
    #Main loop
    #Get delta time events
    while Flags.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Flags.running = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    Flags.running = False
        for i in delta_time_list:
            if i.time_passed():
                i.run()

        #Rendering
        if Counters.game_ticks % FRAME_FREQUENCY == 0:
            #Clear screen
            screen.fill((100,0,0))
            #Draw screen
            handle_fblits()
            screen.fblits(fblits_list)
            #Draw notes
            if Flags.in_game:
                for note_row in note_list:
                    for note in note_row:
                        note.move()

            for i in destroy_list:
                i.destroy()
            destroy_list.clear()

            pygame.display.flip()

        #Next tick
        if Flags.in_game:
            Counters.game_ticks+=1
        Counters.ticks+=1
        clock.tick(TPS_CAP)