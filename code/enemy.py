import pygame 


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, groups, player, obstacle_sprites):
        super().__init__(groups)

        #sprite van flying enemy (placeholder)
        self.image = pygame.image.load('graphics/test_images/wispsprite.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)

        #movement
        self.player = player
        self.speed = 2

        #hp
        self.health = 100
        self.max_health = 100

        #collision
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

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.die()
    
    def die(self):
        self.kill()

    def draw_health_bar(self, surface, offset=None):
        if offset is None:
            offset = pygame.math.Vector2(0, 0)
        
        health_bar_width = self.rect.width
        health_bar_height = 5
        health_bar_x = self.rect.x - offset.x
        health_bar_y = self.rect.y - offset.y - health_bar_height - 2

        # Calculate health ratio
        health_ratio = self.health / self.max_health

        # Draw background bar (red)
        pygame.draw.rect(surface, (255, 0, 0), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))

        # Draw foreground bar (green)
        pygame.draw.rect(surface, (0, 255, 0), (health_bar_x, health_bar_y, health_bar_width * health_ratio, health_bar_height))

    