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

        # Hotbar setup
        self.hotbar_slots = ['dagger', 'revolver', 'shotgun', 'sniper']
        self.hotbar_keys = ['2', '3', '4', '5',]
        
        # Laad icons
        graphics_path = BASE_DIR.parent / "graphics" / "weapons"
        self.weapon_icons = {
            'dagger': pygame.image.load(graphics_path / "dagger.png").convert_alpha(),
            'revolver': pygame.image.load(graphics_path / "revolver.png").convert_alpha(),
            'shotgun': pygame.image.load(graphics_path / "shotgun.png").convert_alpha(),
            'sniper': pygame.image.load(graphics_path / "sniper.png").convert_alpha(),
        }

        # Schaal icons
        for key in self.weapon_icons:
            self.weapon_icons[key] = pygame.transform.scale(
                self.weapon_icons[key], (50, 20)
            )


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

 
    def display_hotbar(self, player):
        """
        Displayt een hotbar met alle wapens, en highlight het nummer van het wapen
        
        Args: 
            player : player info is nodig voor informatie welk wapen geselecteerd is
        """
        screen_width = self.display_surface.get_width()
        y = self.display_surface.get_height() - 60 #y positie is 60 px van de grond

        spacing = 70 #pixels tussen elk icon
        total_width = len(self.hotbar_slots) * spacing 
        start_x = 40

        for index, weapon in enumerate(self.hotbar_slots):
            x = start_x + index * spacing # x locatie van de hotbar

            # Teken icon
            icon = self.weapon_icons[weapon]
            icon_rect = icon.get_rect(center=(x, y))
            self.display_surface.blit(icon, icon_rect)

            # Highlight alleen het nummer wanneer geselecteerd
            is_selected = (weapon == player.weapon)

            color = (255, 215, 0) if is_selected else (180, 180, 180) #maakt nummer geel als selected is

            key_text = self.font.render(self.hotbar_keys[index], True, color)

            # zet nummer onder de icons
            text_rect = key_text.get_rect(center=(x, y + 30))
            self.display_surface.blit(key_text, text_rect)


    def display(self, player):
        """
        Update en rendert de volledige UI, inclusief de vloeiende gezondheidsbalk.

        Args:
            player (Player): Het player-object om de health van te lezen.
        """
        if self.displayed_health is None:
            self.displayed_health = player.health

        # verplaatst de lag-balk naar de werkelijke gezondheid
        # De factor 0.08 bepaalt de snelheid van de animatie
        self.displayed_health += (player.health - self.displayed_health) * 0.08

        #BG BAR
        self.show_bar(player.stats['health'], player.stats['health'], self.bar_rect, (90, 0, 0))

        #Teken de 'lag' achtergrondbalk (vaak een lichtere kleur)
        self.show_bar(self.displayed_health, player.stats['health'], self.bar_rect, (255, 200, 200))

        #Teken de werkelijke gezondheidsbalk
        self.show_bar(player.health, player.stats['health'], self.bar_rect, HEALTH_COLOR)

        #Teken de omlijsting/frame op de voorgrond
        self.display_surface.blit(self.bg, self.player_health_bar_rect.topleft)

        self.display_hotbar(player)