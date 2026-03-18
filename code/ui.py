import pygame
from settings import *

class UI:
    """
    Beheert de visuele weergave van spelersstatistieken zoals de gezondheidsbalk.

    Deze klasse ondersteunt 'smooth interpolation' voor de gezondheidsbalk, 
    waardoor de balk niet direct verspringt bij schade, maar vloeiend naar 
    de nieuwe waarde beweegt (ook wel een 'lag bar' genoemd).

    Attributes:
        display_surface (pygame.Surface): Het hoofdscherm waarop de UI getekend wordt.
        font (pygame.font.Font): Het lettertype voor tekstuele UI-elementen.
        bg (pygame.Surface): De visuele omlijsting/frame van de gezondheidsbalk.
    """

    def __init__(self, display_surface):
        """
        Initialiseert de UI met health-bar configuraties en afbeeldingen.

        Args:
            display_surface (pygame.Surface): De hoofd-display surface.
        """
        self.display_surface = display_surface
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        # Configuratie gezondheidsbalk
        self.player_health_bar_rect = pygame.Rect(50, 10, PLAYER_HEALTH_BAR_WIDTH, PLAYER_BAR_HEIGHT)
        self.displayed_health = None # Wordt gebruikt voor de 'lag' animatie

        # Bepaal padding zodat de balk netjes in het frame valt
        self.bar_padding_x = 40
        self.bar_padding_y = 5

        self.bar_rect = pygame.Rect(
            self.player_health_bar_rect.x + self.bar_padding_x,
            self.player_health_bar_rect.y + self.bar_padding_y,
            PLAYER_HEALTH_BAR_WIDTH - self.bar_padding_x,
            PLAYER_BAR_HEIGHT - self.bar_padding_y
        )

        # Laad en schaal de health-bar interface
        graphics_path = BASE_DIR.parent / "graphics" / "other_images"
        self.bg = pygame.image.load(graphics_path / "health_bar.png").convert_alpha()
        self.bg = pygame.transform.scale(self.bg, (PLAYER_HEALTH_BAR_WIDTH, PLAYER_BAR_HEIGHT))

    def show_bar(self, current_amount, max_amount, bg_rect, color):
        """
        Tekent een rechthoekige balk gebaseerd op de ratio van huidige naar maximale gezondheid.

        Args:
            current_amount (float): De waarde die getekend moet worden.
            max_amount (int): De maximale waarde.
            bg_rect (pygame.Rect): De positie en afmeting van de balk.
            color (tuple): RGB-waarde voor de kleur van de balk.
        """
        ratio = current_amount / max_amount
        current_width = bg_rect.width * ratio
        current_rect = bg_rect.copy()
        current_rect.width = current_width

        pygame.draw.rect(self.display_surface, color, current_rect)

    def display(self, player):
        """
        Update en rendert de volledige UI, inclusief de vloeiende gezondheidsbalk.

        Args:
            player (Player): Het player-object om de gezondheid van te lezen.
        """
        if self.displayed_health is None:
            self.displayed_health = player.health

        # verplaatst de lag-balk naar de werkelijke gezondheid
        # De factor 0.08 bepaalt de snelheid van de animatie
        self.displayed_health += (player.health - self.displayed_health) * 0.08

        #Teken de 'lag' achtergrondbalk (vaak een lichtere kleur)
        self.show_bar(self.displayed_health, player.stats['health'], self.bar_rect, (255, 200, 200))

        #Teken de werkelijke gezondheidsbalk
        self.show_bar(player.health, player.stats['health'], self.bar_rect, HEALTH_COLOR)

        #Teken de omlijsting/frame op de voorgrond
        self.display_surface.blit(self.bg, self.player_health_bar_rect.topleft)