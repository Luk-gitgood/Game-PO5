import pygame
from settings import *

graphics_path = BASE_DIR.parent / 'graphics' / 'other_images'

running = False
screen_ratio = 0

pygame.init()
pygame.mixer.init()
global_volume = 0.3
pygame.mixer.music.set_volume(global_volume)

MENU_SIZE = (800,800)
menu_screen = pygame.display.set_mode(MENU_SIZE)
bg_image = pygame.image.load("graphics/other_images/test_menu_bg.png").convert()
bg_image = pygame.transform.scale(bg_image, MENU_SIZE)
st_bg_image = pygame.image.load("graphics/other_images/menu_settings_bg.png").convert()
st_bg_image = pygame.transform.scale(st_bg_image, MENU_SIZE)
pygame.display.set_caption("Insolitum - Menu")
pygame.display.set_icon(pygame.image.load(graphics_path / 'icon_insolitum.png'))

#settings for font styles, sizes and colors
FONT = pygame.font.SysFont("arial", 40)
SMALL_FONT = pygame.font.SysFont("arial", 28)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

#button class, allows to put buttons anywhere in the menu
class Button:

    def __init__(self, x, y, width, height, image_normal, image_hovered):
        self.n_image = pygame.image.load(image_normal)
        self.h_image = pygame.image.load(image_hovered)
        self.image = self.n_image

        self.rect = pygame.Rect(x, y, width, height)

    def draw(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.image = self.h_image
        else:
            self.image = self.n_image

        menu_screen.blit(self.image, self.rect)

    def pressed(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(pygame.mouse.get_pos())

#renders any test in x,y
def draw_text(text,x, y):
    text_surface = FONT.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=(x, y))
    menu_screen.blit(text_surface, text_rect)


def main_menu():
    global running
    clock = pygame.time.Clock()

    start_button = Button(100, 300, 80, 40, 'graphics/other_images/start_button.png', 'graphics/other_images/start_button_hover.png')
    settings_button = Button(100, 400, 80, 40, 'graphics/other_images/settings_button.png', 'graphics/other_images/settings_button_hover.png')
    cancel_button = Button(100, 500, 80, 40, 'graphics/other_images/quit_button.png', 'graphics/other_images/quit_button_hover.png')

    in_menu = True

    while in_menu:
        menu_screen.blit(bg_image, (0, 0))
        draw_text("INSOLITUM", 400, 150)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if start_button.pressed(event):
                running = True
                in_menu = False

            if settings_button.pressed(event):
                settings_menu()

            if cancel_button.pressed(event):
                pygame.quit()
                exit()

        start_button.draw()
        settings_button.draw()
        cancel_button.draw()

        pygame.display.update()
        clock.tick(60)


def settings_menu():
    global screen_ratio
    clock = pygame.time.Clock()

    sizes = pygame.display.get_desktop_sizes()

    back_button = Button(200, 650, 200, 60, 'graphics/other_images/settings_back_button.png', 'graphics/other_images/settings_back_button_hover.png')
    next_ratio = Button( 150, 250, 300, 60, 'graphics/other_images/start_button.png', 'graphics/other_images/start_button_hover.png')
    volume_up = Button(150, 400, 300, 60, 'graphics/other_images/start_button.png', 'graphics/other_images/start_button_hover.png')
    volume_down = Button(150, 480, 300, 60, 'graphics/other_images/start_button.png', 'graphics/other_images/start_button_hover.png')

    current_ratio_index = screen_ratio

    in_settings = True


    while in_settings:
        menu_screen.blit(st_bg_image, (0, 0))
        draw_text("SETTINGS", 120, 150)

        selected_ratio = SMALL_FONT.render(
            f"Resolution: {sizes[current_ratio_index]}", False, BLUE)
        menu_screen.blit(selected_ratio, (120, 200))

        volume_text = SMALL_FONT.render(
            f"Volume: {global_volume}", False, BLUE)
        menu_screen.blit(volume_text, (220, 350))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            #applies changes to selected aspect ratio and goes back to menu
            if back_button.pressed(event):
                screen_ratio = current_ratio_index
                in_settings = False

            #goes through possible aspect ratio's, depending on the monitor size
            if next_ratio.pressed(event):
                current_ratio_index += 1
                if current_ratio_index >= len(sizes):
                    current_ratio_index = 0


            #working on it, doesn't do anything for now
            if volume_up.pressed(event):
                pass
                #pygame.mixer.music.set_volume(global_volume)

            if volume_down.pressed(event):
                pass
                #pygame.mixer.music.set_volume(global_volume)

        #creates the buttons in the settings menu
        next_ratio.draw()
        volume_up.draw()
        volume_down.draw()
        back_button.draw()

        pygame.display.update()
        clock.tick(60)


# run menu before main game loop continues
main_menu()