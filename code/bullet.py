import pygame
import math
from settings import *


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, angle, groups, obstacle_sprites, attackable_sprites, speed, lifetime, damage):
        super().__init__(groups)

        #graphics
        self.image = pygame.Surface((12, 6), pygame.SRCALPHA)

        #gives outer color
        pygame.draw.ellipse(self.image, (255, 100, 0), [0, 0, 12, 6])
        #gives inner color
        pygame.draw.ellipse(self.image, (255, 255, 150), [2, 1, 8, 4])

        self.image = pygame.transform.rotate(self.image, -angle)

        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(pos)
        self.obstacle_sprites = obstacle_sprites
        self.attackable_sprites = attackable_sprites

        #covement
        #convert angle to a direction vector
        rad = math.radians(angle)
        self.direction = pygame.math.Vector2(math.cos(rad), math.sin(rad))
        self.speed = speed

        #lifespan (to prevent bullets traveling forever)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = lifetime

        #damage
        self.damage = damage

    def check_collision(self):
        for sprite in self.obstacle_sprites:
            if sprite.hitbox.colliderect(self.rect):
                self.kill()  # Destroy bullet on impact

    def deal_damage(self):
        for sprite in self.attackable_sprites:
            if sprite.hitbox.colliderect(self.rect):
                sprite.take_damage(self.damage)
                self.kill()

    def update(self):
        #move using high precision floats
        self.pos += self.direction * self.speed
        self.rect.center = self.pos

        self.check_collision()
        self.deal_damage()

        #despawn after lifetime (ms) expires
        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()
