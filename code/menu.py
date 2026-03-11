import pygame
from settings import *

class Button:
    def __init__(self, surface, anchor, offset, image_normal, image_hover):
        self.surface = surface

        self.n_image = pygame.image.load(image_normal).convert_alpha()
        self.h_image = pygame.image.load(image_hover).convert_alpha()

        self.image = self.n_image
        self.rect = self.image.get_rect()

        self.anchor = anchor
        self.offset = pygame.Vector2(offset)

        self.update_position()

    def update_position(self):
        surface_rect = self.surface.get_rect()

        anchor_pos = getattr(surface_rect, self.anchor)
        setattr(self.rect, self.anchor, anchor_pos + self.offset)

    def update(self):
        self.get_mouse_pos()
        if self.rect.collidepoint(self.mouse_scaled):
            self.image = self.h_image
        else:
            self.image = self.n_image

    def draw(self):
        self.surface.blit(self.image, self.rect)

    def is_pressed(self, event):
        self.get_mouse_pos()
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(self.mouse_scaled)
        )

    def get_mouse_pos(self):
        #Took next 12 lines from weapon for scaled mouse pos
        #User screen size
        info = pygame.display.Info()
        MONITOR_WIDTH = info.current_w
        MONITOR_HEIGHT = info.current_h

        #Position and direction logic
        scale_x = BASE_SCREEN_WIDTH / MONITOR_WIDTH
        scale_y = BASE_SCREEN_HEIGHT / MONITOR_HEIGHT
        mouse_pos = pygame.mouse.get_pos()

        #convert mouse from real screen resolution to base resolution
        self.mouse_scaled = pygame.math.Vector2(mouse_pos[0] * scale_x,mouse_pos[1] * scale_y)


class MainMenu:
    def __init__(self, game):
        self.game = game
        self.display = game.game_surface

        buttons_path = BASE_DIR.parent / "graphics" / "buttons"
        other_images_path = BASE_DIR.parent / "graphics" / "other_images"

        self.bg = pygame.image.load(other_images_path / "test_mainmenu_bg.png").convert()
        self.bg = pygame.transform.scale(self.bg, (BASE_SCREEN_WIDTH, BASE_SCREEN_HEIGHT))
        self.title = pygame.image.load(other_images_path / 'title.png').convert_alpha()

        #Store buttons in a list
        self.buttons = [
            Button(self.display, 'center', (0, 0), buttons_path / 'play01.png', buttons_path / 'play02.png'),
            Button(self.display, 'center', (0, 100), buttons_path / 'video01.png', buttons_path / 'video02.png'),
            Button(self.display, 'center', (0, 200), buttons_path / 'quit01.png', buttons_path / 'quit02.png')
        ]

        #Name them for easy event checking
        self.start_button = self.buttons[0]
        self.settings_button = self.buttons[1]
        self.quit_button = self.buttons[2]

        self.font = pygame.font.SysFont("arial", 40)

    def handle_events(self, event):
        if self.start_button.is_pressed(event):
            self.game.set_state("game")
        elif self.settings_button.is_pressed(event):
            self.game.set_state("settings")
        elif self.quit_button.is_pressed(event):
            self.game.running = False

    def update(self):
        for button in self.buttons:
            button.update()

    def draw(self):
        self.display.blit(self.bg, (0, 0))
        self.display.blit(self.title, (510, 70))
        
        for button in self.buttons:
            button.draw()


class SettingsMenu:
    def __init__(self, game):
        self.game = game
        self.display = game.game_surface
        
        buttons_path = BASE_DIR.parent / "graphics" / "buttons"
        other_images_path = BASE_DIR.parent / "graphics" / "other_images"

        #Background and Overlay setup
        self.bg = pygame.image.load(other_images_path / "menu_settings_bg.png").convert()
        self.bg = pygame.transform.scale(self.bg, (BASE_SCREEN_WIDTH, BASE_SCREEN_HEIGHT))
        self.overlay = pygame.Surface((BASE_SCREEN_WIDTH, BASE_SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((50, 50, 50, 30))

        self.sizes = pygame.display.get_desktop_sizes()
        self.current_ratio_index = 0
        self.font = pygame.font.SysFont("arial", 28)

        #Store buttons in a list
        self.buttons = [
            Button(self.display, 'center', (0, 200), buttons_path / 'back01.png', buttons_path / 'back02.png'),
            Button(self.display, 'center', (0, 100), buttons_path / 'restart01.png', buttons_path / 'restart02.png'),
            Button(self.display, 'topleft', (100, 400), buttons_path / 'option01.png', buttons_path / 'option02.png')
        ]

        #Name them for easy event checking
        self.back_button = self.buttons[0]
        self.restart_button = self.buttons[1]
        self.next_ratio = self.buttons[2]

    def handle_events(self, event):
        if self.back_button.is_pressed(event):
            self.game.set_state(self.game.previous_state)

        elif self.next_ratio.is_pressed(event):
            self.current_ratio_index = (self.current_ratio_index + 1) % len(self.sizes)

        elif self.restart_button.is_pressed(event):
            self.game.restart_level()
            self.game.set_state('menu')

    def update(self):
        for button in self.buttons:
            button.update()

    def draw(self):
        self.display.blit(self.overlay, (0, 0))

        # Render resolution text
        text = self.font.render(
            f"Resolution: {self.sizes[self.current_ratio_index]}",
            True, (0, 0, 255)
        )
        self.display.blit(text, (120, 200))

        for button in self.buttons:
            button.draw()