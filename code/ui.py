import pygame
from settings import *

class UI:

	def __init__(self, display_surface):

		#General
		self.display_surface = display_surface
		self.font = pygame.font.Font(UI_FONT,UI_FONT_SIZE)

		#Health bar
		self.player_health_bar_rect = pygame.Rect(10,10, PLAYER_HEALTH_BAR_WIDTH, PLAYER_BAR_HEIGHT)
		self.enemy_health_bar_rect = None


	def show_bar(self, current_amount, max_amount, bg_rect, color):

		#draw bg
		pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)

		#converting stats to pixels
		ratio = current_amount / max_amount
		current_width = bg_rect.width * ratio
		current_rect = bg_rect.copy()
		current_rect.width = current_width

		#drawng bar
		pygame.draw.rect(self.display_surface, color, current_rect)
		pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)


	def display(self, player):
		#player health bar
		self.show_bar(player.health, player.stats['health'], self.player_health_bar_rect, HEALTH_COLOR)

