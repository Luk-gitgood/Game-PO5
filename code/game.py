import pygame
from settings import *
from level import Level
from menu import *
from audio import AudioManager


class Game:
    def __init__(self):
        pygame.init()

        #Window setup
        pygame.display.set_caption("Insolitum")

        graphics_path = BASE_DIR.parent / "graphics" / "other_images"
        pygame.display.set_icon(pygame.image.load(graphics_path / "icon_insolitum.png"))

        pygame.mouse.set_cursor(pygame.cursors.diamond)

        #monitor info
        info = pygame.display.Info()
        self.MONITOR_WIDTH = info.current_w
        self.MONITOR_HEIGHT = info.current_h

        #display state
        self.is_fullscreen = True
        self.screen = pygame.display.set_mode(
            (self.MONITOR_WIDTH, self.MONITOR_HEIGHT),pygame.FULLSCREEN)

        #internal game surface (fixed resolution)
        self.game_surface = pygame.Surface((BASE_SCREEN_WIDTH, BASE_SCREEN_HEIGHT))

        #clock
        self.clock = pygame.time.Clock()
        self.running = True

        #game state
        self.state = None
        self.previous_state = None



        #create systems
        self.menu = MainMenu(self)
        self.settings = SettingsMenu(self)

        #game objects
        self.level = Level(self.game_surface)

        #audio objects
        self.audio_dict = {
            "menu" : MUSIC_PATH / "mainmenu_music.ogg",
            "level1": MUSIC_PATH / "Insolitum_music1.ogg",
            "settings": MUSIC_PATH / "elevator_bossanova.ogg"
        }
        self.audio = AudioManager(self.audio_dict)

        self.set_state("menu")

    def set_state(self, new_state):
        self.previous_state = self.state
        self.state = new_state
    
        if new_state == "menu":
            self.audio.play("menu")

        elif new_state == "game":
            self.audio.play("level1")

        elif new_state == "settings":
            self.audio.play("settings")
        #later more options for different music


    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen

        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((self.MONITOR_WIDTH, self.MONITOR_HEIGHT),pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((BASE_SCREEN_WIDTH, BASE_SCREEN_HEIGHT),pygame.RESIZABLE)

    def handle_events(self):
        for event in pygame.event.get():
    
            #always handle quit
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
                    if event.key == pygame.K_ESCAPE:
                        self.set_state('settings')
    
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
        scaled_surface = pygame.transform.scale(
            self.game_surface,
            self.screen.get_size()
        )
        self.screen.blit(scaled_surface, (0, 0))

        if self.state == "menu":
            self.menu.draw()
    
        elif self.state == "settings":
            self.settings.draw()

        pygame.display.update()


    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()

    def restart_level(self):
        self.level = Level(self.game_surface)
        self.audio.stop()


if __name__ == "__main__":
    game = Game()
    game.run()
