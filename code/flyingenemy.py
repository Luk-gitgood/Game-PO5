import pygame


class FlyingEnemy(pygame.sprite.Sprite):
    def __init__(self, pos, groups, player, obstacle_sprites):
        super().__init__(groups)

        # sprite van flying enemy (placeholder)
        self.image = pygame.image.load('../graphics/test_images/wispsprite.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)

        # movement
        self.direction = pygame.math.Vector2()
        self.player = player
        self.speed = 2

        # hp
        self.health = 50

        # collision
        self.obstacle_sprites = obstacle_sprites
        self.hitbox = self.rect.inflate(0,0)

    def update(self):
        self.move_towards_player()

    def move_towards_player(self):
        self.direction = pygame.math.Vector2(
            self.player.rect.centerx - self.rect.centerx,
            self.player.rect.centery - self.rect.centery
        )

        if self.direction.length() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * self.speed
        self.check_collision('horizontal')

        self.hitbox.y += self.direction.y * self.speed
        self.check_collision('vertical')

        self.rect.center = self.hitbox.center

    def check_collision(self, direction):
        if direction == 'horizontal':
            for obstacle in self.obstacle_sprites:
                if obstacle.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:  # moving right
                        self.hitbox.right = obstacle.hitbox.left
                    if self.direction.x < 0:  # moving left
                        self.hitbox.left = obstacle.hitbox.right

        if direction == 'vertical':
            for obstacle in self.obstacle_sprites:
                if obstacle.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:
                        self.hitbox.bottom = obstacle.hitbox.top
                        self.direction.y = 0

                    if self.direction.y < 0:
                        self.hitbox.top = obstacle.hitbox.bottom
                        self.direction.y = 0

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.die()

    def die(self):
        self.kill()