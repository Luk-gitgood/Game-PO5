import pygame
from spritesheets import SpriteSheet
from entity import Entity
from settings import *


class FlyingEnemy(Entity):

    def __init__(self, pos, groups, player, obstacle_sprites):
        super().__init__(groups)

        # Animations
        graphics_path = BASE_DIR.parent / 'graphics' / 'animations' / 'bat_character'
        self.enemy_scale = 1.5
        self.animation_steps = {'idle': 4, 'fly_left': 4, 'fly_up': 4, 'fly_right': 4,
                                'death': 11}  # amount of frames in each animation
        self.animation_speeds = {'idle': 0.15, 'fly_left': 0.15, 'fly_up': 0.15, 'fly_right': 0.15, 'death': 0.25}

        # Load frames immediately
        self.load_animation_frames(graphics_path)

        self.image = self.frames[self.action][0]
        self.rect = self.frames[self.action][0].get_rect(topleft = pos)
        self.player = player
        self.speed = 2
        
        # hp
        self.health = 50

        # collision
        self.obstacle_sprites = obstacle_sprites
        self.hitbox = self.rect.inflate(0,0)
        self.dying = False



    def load_animation_frames(self, graphics_path):
        # Preload all animations so they are ready when player shoots
        sheets = {
            'idle': SpriteSheet(pygame.image.load(graphics_path / 'bat_idle.png').convert_alpha()),
            'fly_left': SpriteSheet(pygame.image.load(graphics_path / 'flying_left.png').convert_alpha()),
            'fly_up': SpriteSheet(pygame.image.load(graphics_path / 'flying_up.png').convert_alpha()),
            'fly_right': SpriteSheet(pygame.image.load(graphics_path / 'flying_right.png').convert_alpha()),
            'death': SpriteSheet(pygame.image.load(graphics_path / 'bat_death.png').convert_alpha())

        }

        for action, sheet in sheets.items():
            self.frames[action] = [sheet.get_image(i, IMAGE_WIDTH, IMAGE_HEIGHT, self.enemy_scale) for i in range(self.animation_steps[action])]

    def move_towards_player(self):
        self.direction.x = self.player.rect.centerx - self.rect.centerx
        self.direction.y = self.player.rect.centery - self.rect.centery

        if self.direction.length() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * self.speed
        self.check_collision('horizontal')

        self.hitbox.y += self.direction.y * self.speed
        self.check_collision('vertical')

        self.rect.center = self.hitbox.center

    def update_action(self):
        if self.dying:
            return

        if self.direction.length() == 0:
            self.action = 'idle'
        elif abs(self.direction.x) > abs(self.direction.y):
            if self.direction.x > 0:
                self.action = 'fly_left'
            else:
                self.action = 'fly_right'
        else:
            self.action = 'fly_up'

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
        if self.dying:
            return

        self.health -= amount
        if self.health <= 0:
            self.dying = True
            self.action = 'death'
            self.frame_index = 0
            self.speed = 0

    def update(self):
        if not self.dying:
            self.move_towards_player()
            self.update_action()
        self.animate()
