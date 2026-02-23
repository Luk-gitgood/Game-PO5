import pygame
import time

running = False

pygame.init()
screen_ratio = 0

while not running:
    time.sleep(0.5)
    menu_action = input("\ntype 'start' to start\n"
                        "type 'settings' to open settings\n"
                        "type 'cancel' to exit\n"
                        "> ")

    if menu_action == 'start':
        running = True

    elif menu_action == 'settings':
        print('settings are being opened')
        time.sleep(0.3)

        while True:
            settings_action = input("\ntype 'back' to exit settings \n"
                                    "type 'screen' to switch aspect ratios\n"
                                    "> ")

            if settings_action == 'back':
                break

            elif settings_action == 'screen':
                print("Your available ratio's are: ",pygame.display.get_desktop_sizes())
                time.sleep(0.3)
                chosen_ratio = int(input("choose a ratio with 0,1,2,etc.\n> "))

                if chosen_ratio >= len(pygame.display.get_desktop_sizes()):
                    print('number given is bigger than amount of options')

                else:
                    print('aspect ratio has been applied')
                    screen_ratio = chosen_ratio

            else:
                print('invalid option')

    elif menu_action == 'cancel':
        break

    else:
        print('invalid command')