import pygame
from settings import *

class Button:
    def __init__(self, pos, image_normal, image_hover):
        self.n_image = pygame.image.load(image_normal).convert_alpha()
        self.h_image = pygame.image.load(image_hover).convert_alpha()

        self.image = self.n_image
        self.rect = self.image.get_rect(topleft=pos)

    def update(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.image = self.h_image
        else:
            self.image = self.n_image

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def is_pressed(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and \
               event.button == 1 and \
               self.rect.collidepoint(event.pos)


class MainMenu:
    def __init__(self, game):
        self.game = game
        self.display = game.screen

        graphics_path = BASE_DIR.parent / "graphics" / "other_images"

        self.bg = pygame.image.load(
            graphics_path / "test_menu_bg.png"
        ).convert()

        self.start_button = Button(
            (100, 300),
            graphics_path / 'start_button.png',
            graphics_path / 'start_button_hover.png'
        )

        self.settings_button = Button(
            (100, 400),
            graphics_path / 'settings_button.png',
            graphics_path / 'settings_button_hover.png'
        )

        self.quit_button = Button(
            (100, 500),
            graphics_path / 'quit_button.png',
            graphics_path / 'quit_button_hover.png'
        )

        self.font = pygame.font.SysFont("arial", 40)

    def handle_events(self, event):
        if self.start_button.is_pressed(event):
            self.game.state = "game"

        if self.settings_button.is_pressed(event):
            self.game.state = "settings"

        if self.quit_button.is_pressed(event):
            self.game.running = False

    def update(self):
        self.start_button.update()
        self.settings_button.update()
        self.quit_button.update()

    def draw(self):
        self.display.blit(self.bg, (0, 0))

        title = self.font.render("INSOLITUM", True, (255,255,255))
        self.display.blit(title, (400, 150))

        self.start_button.draw(self.display)
        self.settings_button.draw(self.display)
        self.quit_button.draw(self.display)


class SettingsMenu:
    def __init__(self, game):
        self.game = game
        self.display = game.screen
        
        graphics_path = BASE_DIR.parent / "graphics" / "other_images"

        self.bg = pygame.image.load(
            graphics_path / "menu_settings_bg.png"
        ).convert()

        self.sizes = pygame.display.get_desktop_sizes()
        self.current_ratio_index = 0

        self.back_button = Button(
            (200, 650),
            graphics_path / 'settings_back_button.png',
            graphics_path / 'settings_back_button_hover.png'
        )

        self.next_ratio = Button(
            (150, 250),
            graphics_path / 'start_button.png',
            graphics_path / 'start_button_hover.png'
        )

        self.font = pygame.font.SysFont("arial", 28)

    def handle_events(self, event):
        if self.back_button.is_pressed(event):
            self.game.state = "menu"

        if self.next_ratio.is_pressed(event):
            self.current_ratio_index += 1
            if self.current_ratio_index >= len(self.sizes):
                self.current_ratio_index = 0

    def update(self):
        self.back_button.update()
        self.next_ratio.update()

    def draw(self):
        self.display.blit(self.bg, (0, 0))

        text = self.font.render(
            f"Resolution: {self.sizes[self.current_ratio_index]}",
            True,
            (0,0,255)
        )

        self.display.blit(text, (120, 200))

        self.next_ratio.draw(self.display)
        self.back_button.draw(self.display) 
        