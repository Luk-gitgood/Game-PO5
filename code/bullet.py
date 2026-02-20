import pygame
import math
from settings import *


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, angle, groups, obstacle_sprites, speed, lifetime):
        super().__init__(groups)

        # Graphics (You can replace this with an image load)
        self.image = pygame.Surface((10, 4))
        self.image.fill('yellow')
        self.image = pygame.transform.rotate(self.image, -angle)

        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(pos)
        self.obstacle_sprites = obstacle_sprites

        # Movement
        # Convert angle to a direction vector
        rad = math.radians(angle)
        self.direction = pygame.math.Vector2(math.cos(rad), math.sin(rad))
        self.speed = speed

        # Lifespan (to prevent bullets traveling forever)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = lifetime

    def check_collision(self):
        for sprite in self.obstacle_sprites:
            if sprite.hitbox.colliderect(self.rect):
                self.kill()  # Destroy bullet on impact

    def update(self):
        # Move using high precision floats
        self.pos += self.direction * self.speed
        self.rect.center = self.pos

        self.check_collision()

        # Despawn after lifetime (ms) expires
        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()
