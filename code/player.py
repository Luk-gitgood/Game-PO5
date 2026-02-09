import pygame
from settings import *


class Player(pygame.sprite.Sprite):

    def __init__(self, pos, groups, obstacle_sprites):
        super().__init__(groups)
        self.image = pygame.image.load('../graphics/test_images/knight_idle.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(0, 0)
        self.prev_hitbox = None

        self.obstacle_sprites = obstacle_sprites

        self.direction = pygame.math.Vector2()
        self.on_ground = False
        self.drop_timer = 0
        self.speed = 2
        self.gravity = 0.4
        self.jump_speed = -11
        self.jump_held = False
        self.jump_cut_multiplier = 0.7
        self.coyote_timer = 0.1


    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_d]:
            if self.direction.x < 0:
                self.direction.x = 0
            elif self.direction.x < 2:
                self.direction.x += 0.3
        elif keys[pygame.K_a]:
            if self.direction.x > 0:
                self.direction.x = 0
            elif self.direction.x > -2:
                self.direction.x += -0.3
        else:
            self.direction.x = 0

        if keys[pygame.K_SPACE]:
            if not self.jump_held:
                self.jump()
            self.jump_held = True
        else:
            if self.jump_held:
                self.cut_jump()
            self.jump_held = False

        if keys[pygame.K_s] and self.on_ground:
            self.drop_timer = 0.2
            self.direction.y = 1


    def move_horizontal(self, speed):
        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.rect.center = self.hitbox.center


    def apply_gravity(self):

        if self.on_ground:
            self.coyote_timer = 0.1
        else:
            self.coyote_timer -= 1/60

        self.on_ground = False
        self.direction.y += self.gravity * 1.3
        self.hitbox.y += self.direction.y
        self.collision('vertical')
        self.rect.center = self.hitbox.center


    def jump(self):
        if self.coyote_timer > 0:
            self.direction.y = self.jump_speed
            self.coyote_timer = 0


    def cut_jump(self):
        if self.direction.y < 0:
            self.direction.y *= self.jump_cut_multiplier


    def collision(self, direction):
        if direction == 'horizontal':
            for obstacle in self.obstacle_sprites:

                #Pass through platforms horizontally
                if obstacle.sprite_type == 'platform_top':
                    continue

                if obstacle.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0 : #moving right
                        self.hitbox.right = obstacle.hitbox.left
                    if self.direction.x < 0: #moving left
                        self.hitbox.left = obstacle.hitbox.right

        if direction == 'vertical':
            for obstacle in self.obstacle_sprites:
                if obstacle.hitbox.colliderect(self.hitbox):

                    if self.direction.y > 0:

                        if obstacle.sprite_type == 'platform_top':

                            if self.drop_timer > 0:
                                continue

                            elif self.prev_hitbox.bottom <= obstacle.hitbox.top:
                                self.hitbox.bottom = obstacle.hitbox.top
                                self.direction.y = 0
                                self.on_ground = True
                        else:
                            self.hitbox.bottom = obstacle.hitbox.top
                            self.direction.y = 0
                            self.on_ground = True

                    if self.direction.y < 0:
                        if obstacle.sprite_type != 'platform_top':
                            self.hitbox.top = obstacle.hitbox.bottom
                            self.direction.y = 0


    def update(self):
        self.prev_hitbox = self.hitbox.copy()  #store old pos
        self.drop_timer = max(0, self.drop_timer - 1/60)
        self.input()
        self.move_horizontal(self.speed)
        self.apply_gravity()

