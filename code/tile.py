import pygame
from settings import *


class Tiles(pygame.sprite.Sprite):

    def __init__(self, pos, groups, sprite_type, surface=pygame.Surface((TILE_SIZE, TILE_SIZE))):
        super().__init__(groups)
        self.sprite_type = sprite_type
        self.image = surface
        self.rect = self.image.get_rect(topleft = pos)

        if self.sprite_type == 'surface':
            #Changing hitbox using inflate(BAD:<)
            self.hitbox = self.rect.inflate(0, 0)

        elif self.sprite_type == 'platform_top':
            self.hitbox = self.rect.inflate(0, 0)
        
        elif self.sprite_type == 'damage':
            self.hitbox = pygame.Rect(self.rect.left, self.rect.bottom - 16, 32, 16)

        else:
            self.hitbox = self.rect

