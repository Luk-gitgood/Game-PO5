import pygame
from settings import *


class Tiles(pygame.sprite.Sprite):

    def __init__(self, pos, groups, sprite_type, surface=pygame.Surface((TILE_SIZE, TILE_SIZE))):
        super().__init__(groups)
        self.sprite_type = sprite_type
        self.image = surface
        self.rect = self.image.get_rect(topleft = pos)

        if self.sprite_type == 'surf' or 'b_top':
            self.hitbox = self.rect.inflate(-30, -30)
        else:
            self.hitbox = self.rect.inflate(0,0)

