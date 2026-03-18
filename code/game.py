import pygame
from settings import *
from level import Level
from menu import *
from audio import AudioManager

class Game:
    """
    Alle pydoc staat in het Nederlands, maar sommige comments staan nog in het engels. 
    De hoofdcontroller van de game 'Insolitum'.


    Deze klasse beheert de core game-loop, de window instellingen (inclusief fullscreen),
    het schakelen tussen verschillende toestanden (states) zoals menu's en gameplay,
    en het aansturen van de audio- en levelsystemen.

    Attributes:
        screen (pygame.Surface): Het primaire display-oppervlak (window).
        game_surface (pygame.Surface): Een intern oppervlak met vaste resolutie voor schaling.
        state (str): De huidige status van de game (bijv. 'menu', 'game', 'settings').
        running (bool): Vlag die bepaalt of de game-loop actief blijft.
        level (Level): Het huidige actieve level-object.
        audio (AudioManager): Het systeem dat muziek en geluidseffecten beheert.
    """

    def __init__(self):
        """
        Initialiseert het Pygame-framework, het venster, de audio en de game systemen.
        """
        pygame.init()

        # Venster instellingen
        pygame.display.set_caption("Insolitum")

        graphics_path = BASE_DIR.parent / "graphics" / "other_images"
        pygame.display.set_icon(pygame.image.load(graphics_path / "icon_insolitum.png"))

        pygame.mouse.set_cursor(pygame.cursors.diamond)

        # Monitor info
        info = pygame.display.Info()
        self.MONITOR_WIDTH = info.current_w
        self.MONITOR_HEIGHT = info.current_h

        # Display status
        self.is_fullscreen = True
        self.screen = pygame.display.set_mode(
            (self.MONITOR_WIDTH, self.MONITOR_HEIGHT), pygame.FULLSCREEN)

        # Intern oppervlak (vaste resolutie voor consistente rendering)
        self.game_surface = pygame.Surface((BASE_SCREEN_WIDTH, BASE_SCREEN_HEIGHT))

        # Tijdbeheer
        self.clock = pygame.time.Clock()
        self.running = True

        # Game status
        self.state = None
        self.previous_state = None

        # Systemen aanmaken
        self.menu = MainMenu(self)
        self.settings = SettingsMenu(self)

        # Game objecten
        self.level = Level(self.game_surface)

        # Audio config
        self.audio_dict = {
            "menu" : MUSIC_PATH / "mainmenu_music.ogg",
            "level1": MUSIC_PATH / "Insolitum_music1.ogg",
            "settings": MUSIC_PATH / "elevator_bossanova.ogg"
        }
        self.audio = AudioManager(self.audio_dict)

        self.set_state("menu")

    def set_state(self, new_state):
        """
        Wisselt de huidige toestand van de game en past de muziek daarop aan.

        Args:
            new_state (str): De nieuwe status (bijv. 'menu', 'game' of 'settings').
        """
        self.previous_state = self.state
        self.state = new_state
        
        if new_state == "menu":
            self.audio.play("menu")
        elif new_state == "game":
            self.audio.play("level1")
        elif new_state == "settings":
            self.audio.play("settings")


    def toggle_fullscreen(self):
        """
        Schakelt tussen de volledige schermweergave en de windowed mode.
        """
        self.is_fullscreen = not self.is_fullscreen

        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((self.MONITOR_WIDTH, self.MONITOR_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((BASE_SCREEN_WIDTH, BASE_SCREEN_HEIGHT), pygame.RESIZABLE)


    def handle_events(self):
        """
        Verwerkt alle input-events van de gebruiker (toetsenbord, muis, afsluiten).
        De verwerking is afhankelijk van de huidige gamestate.
        """
        for event in pygame.event.get():
            # Algemeen: Afsluiten
            if event.type == pygame.QUIT:
                self.running = False
    
            # State-specifieke handeling
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
        """
        Update de logica van de game op basis van de huidige status.
        Bewegingen, AI, en spelregels in het level.
        """
        if self.state == "menu":
            self.menu.update()

        elif self.state == "settings":
            self.settings.update()

        elif self.state == "game":
            self.game_surface.fill((0, 0, 0))
            self.level.run()

    def draw(self):
        """
        Tekent alle visuele elementen naar het scherm.
        Schaald de interne game_surface naar de huidige window grootte.
        """
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
        """
        De hoofdloop van het programma die events, updates en rendering coördineert
        met een constante framerate van 60 Ticks/ Frames Per Second.
        """
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()

    def restart_level(self):
        """
        Reset het huidige level door een nieuwe instance van Level aan te maken
        en stopt de huidige muziek.
        """
        self.level = Level(self.game_surface)
        self.audio.stop()


if __name__ == "__main__": 
    game = Game()
    game.run()