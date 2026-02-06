import pygame 

import pygame

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, groups, player, obstacle_sprites):
        super().__init__(groups)

        # Simple placeholder image
        self.image = pygame.Surface((32, 32))
        self.image.fill((200, 50, 50))  # red box
        self.rect = self.image.get_rect(center=pos)

        # Movement
        self.player = player
        self.speed = 2

        # Collision
        self.obstacle_sprites = obstacle_sprites
        self.hitbox = self.rect.copy()

    def update(self):
        self.move_towards_player()

    def move_towards_player(self):
        direction = pygame.math.Vector2(
            self.player.rect.centerx - self.rect.centerx,
            self.player.rect.centery - self.rect.centery
        )

        if direction.length() != 0:
            direction = direction.normalize()

        self.hitbox.x += direction.x * self.speed
        self.check_collision('horizontal')

        self.hitbox.y += direction.y * self.speed
        self.check_collision('vertical')

        self.rect.center = self.hitbox.center

    def check_collision(self, direction):
        for sprite in self.obstacle_sprites:
            if sprite.rect.colliderect(self.hitbox):
                if direction == 'horizontal':
                    if self.hitbox.centerx > sprite.rect.centerx:
                        self.hitbox.left = sprite.rect.right
                    else:
                        self.hitbox.right = sprite.rect.left
                if direction == 'vertical':
                    if self.hitbox.centery > sprite.rect.centery:
                        self.hitbox.top = sprite.rect.bottom
                    else:
                        self.hitbox.bottom = sprite.rect.top