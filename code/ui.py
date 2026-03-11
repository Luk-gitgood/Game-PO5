import pygame
from settings import *

class UI:

    def __init__(self, display_surface):

        # General
        self.display_surface = display_surface
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        # Health bar
        self.player_health_bar_rect = pygame.Rect(10, 10, PLAYER_HEALTH_BAR_WIDTH, PLAYER_BAR_HEIGHT)
        self.enemy_health_bar_rect = None
        self.displayed_health = None


    def show_bar(self, current_amount, max_amount, bg_rect, color):

        # converting stats to pixels
        ratio = current_amount / max_amount
        current_width = bg_rect.width * ratio
        current_rect = bg_rect.copy()
        current_rect.width = current_width

        # drawing bar
        pygame.draw.rect(self.display_surface, color, current_rect)

        # border
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)


    def display(self, player):

        if self.displayed_health is None:
            self.displayed_health = player.health

        # smoothing
        self.displayed_health += (player.health - self.displayed_health) * 0.08  # speed of slow bar

        # draw background once
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, self.player_health_bar_rect)

        # draw lag bar first
        self.show_bar(self.displayed_health, player.stats['health'], self.player_health_bar_rect, (255, 200, 200))

        # draw real health on top
        self.show_bar(player.health, player.stats['health'], self.player_health_bar_rect, HEALTH_COLOR)