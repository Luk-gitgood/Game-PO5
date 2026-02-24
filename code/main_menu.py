import pygame
import time

running = False

#allows anything with pygame to work
pygame.init()
screen_ratio = 0

# initializes the mixer, which is used to play sounds and music
pygame.mixer.init()
pygame.mixer.music.set_volume(0.3)


while not running:
    time.sleep(0.3)
    menu_action = input("\ntype 'start' to start\n"
                        "type 'settings' to open settings\n"
                        "type 'cancel' to exit\n"
                        "> ")

    if menu_action == 'start':
        print('\ngame is launching...')
        time.sleep(1)
        running = True

    elif menu_action == 'settings':
        print('settings are being opened')
        time.sleep(0.3)

        while True:
            settings_action = input("\ntype 'back' to exit settings \n"
                                    "type 'screen' to switch aspect ratios\n"
                                    "tpe 'audio' to change volume\n"
                                    "> ")

            if settings_action == 'back':
                break

            elif settings_action == 'screen':
                print("Your available ratio's are: ",pygame.display.get_desktop_sizes())
                time.sleep(0.3)
                chosen_ratio = input("choose a ratio with 0,1,2,etc.\n> ")
                if chosen_ratio.isdigit():

                    if  int(chosen_ratio) > len(pygame.display.get_desktop_sizes()) or int(chosen_ratio) < 0:
                        print('input given is bigger than amount of options or is negative')

                    elif 0 <= int(chosen_ratio) < len(pygame.display.get_desktop_sizes()):
                        print('aspect ratio has been applied')
                        screen_ratio = int(chosen_ratio)

                else:
                    print('input is invalid')

            elif settings_action == 'audio':
                selected_volume = float(input('please enter volume between 0 and 1\n(the default is 0.3)\n> '))
                pygame.mixer.volume = selected_volume
                print('the volume has been set to ',selected_volume)

            else:
                print('invalid option')

    elif menu_action == 'cancel':
        break

    else:
        print('invalid command')
