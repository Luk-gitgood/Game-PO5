import pygame
from settings import *
from level import Level
from menu import *


class Game:
    def __init__(self):
        pygame.init()

        #Window setup
        pygame.display.set_caption("Insolitum")

        graphics_path = BASE_DIR.parent / "graphics" / "other_images"
        pygame.display.set_icon(pygame.image.load(graphics_path / "icon_insolitum.png"))

        pygame.mouse.set_cursor(pygame.cursors.diamond)

        #Monitor info
        info = pygame.display.Info()
        self.MONITOR_WIDTH = info.current_w
        self.MONITOR_HEIGHT = info.current_h

        #Display state
        self.is_fullscreen = True
        self.screen = pygame.display.set_mode(
            (self.MONITOR_WIDTH, self.MONITOR_HEIGHT),pygame.NOFRAME)

        #Internal game surface (fixed resolution)
        self.game_surface = pygame.Surface((BASE_SCREEN_WIDTH, BASE_SCREEN_HEIGHT))

        #Clock
        self.clock = pygame.time.Clock()
        self.running = True

        # Game state
        self.state = "menu"

        # Create systems
        self.menu = MainMenu(self)
        self.settings = SettingsMenu(self)

        #Game objects
        self.level = Level(self.game_surface)


    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen

        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((self.MONITOR_WIDTH, self.MONITOR_HEIGHT),pygame.NOFRAME)
        else:
            self.screen = pygame.display.set_mode((BASE_SCREEN_WIDTH, BASE_SCREEN_HEIGHT),pygame.RESIZABLE)


    def handle_events(self):
        for event in pygame.event.get():
    
            #Always handle quit
            if event.type == pygame.QUIT:
                self.running = False
    
            #State specific handling
            if self.state == "menu":
                self.menu.handle_events(event)
    
            elif self.state == "settings":
                self.settings.handle_events(event)
    
            elif self.state == "game":
    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.toggle_fullscreen()
    
                if event.type == pygame.VIDEORESIZE and not self.is_fullscreen:
                    self.screen = pygame.display.set_mode(
                        (event.w, event.h), pygame.RESIZABLE
                    )
    


    def update(self):
        if self.state == "menu":
            self.menu.update()

        elif self.state == "settings":
            self.settings.update()

        elif self.state == "game":
            self.game_surface.fill((0, 0, 0))
            self.level.run()


    def draw(self):
        if self.state == "menu":
            self.menu.draw()
    
        elif self.state == "settings":
            self.settings.draw()
    
        elif self.state == "game":
            scaled_surface = pygame.transform.scale(
                self.game_surface,
                self.screen.get_size()
            )
            self.screen.blit(scaled_surface, (0, 0))
    
        pygame.display.update()


    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
