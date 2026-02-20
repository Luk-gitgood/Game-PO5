import pygame
import math
from spritesheets import SpriteSheet
from settings import *
from bullet import Bullet
import random


class Weapon(pygame.sprite.Sprite):
    def __init__(self, groups, player, obstacle_sprites):
        super().__init__(groups)

        graphics_path = BASE_DIR.parent / 'graphics' / 'weapons'
        self.groups = groups
        self.player = player
        self.obstacle_sprites = obstacle_sprites

        #Static Setup
        full_path = f"{graphics_path}/{self.player.weapon}.png"
        self.original_image = pygame.image.load(full_path).convert_alpha()
        self.flipped_image = pygame.transform.flip(self.original_image, False, True)

        self.image = self.original_image
        self.angle = 0
        self.direction = pygame.math.Vector2()
        self.rect = self.image.get_rect(center=self.player.rect.center)

        #Animation Setup
        self.action = 'idle'
        self.frame_index = 0
        self.frames = {}

        self.weapon_sizes = {'revolver': [38, 20], 'shotgun': [52, 14]}
        self.animation_steps = {'revolver': 7, 'shotgun': 16}
        self.animation_speeds = {'revolver': 0.5, 'shotgun': 0.7}

        #Load frames immediately
        self.load_animation_frames(graphics_path)

    def load_animation_frames(self, path):
        # Preload all animations so they are ready when player shoots
        sheets = {
            'revolver': SpriteSheet(pygame.image.load(path / 'revolver_animation.png').convert_alpha()),
            'shotgun': SpriteSheet(pygame.image.load(path / 'shotgun_animation.png').convert_alpha())
        }

        for name, sheet in sheets.items():
            self.frames[name] = [
                sheet.get_image(i, self.weapon_sizes[name][0], self.weapon_sizes[name][1], 1)
                for i in range(self.animation_steps[name])
            ]

    def shoot(self):
        #Only start animation if player isn't already shooting
        if self.action == 'idle':
            self.action = self.player.weapon
            self.frame_index = 0

            weapon_stats = weapon_data[self.player.weapon]
            for _ in range(weapon_stats['bullet_count']):
                spread = random.uniform(-weapon_stats['spread'], weapon_stats['spread'])
                Bullet(self.rect.center, self.angle + spread, self.groups, self.obstacle_sprites, weapon_stats['speed'],
                       weapon_stats['lifetime'])

            if self.player.weapon == 'shotgun':
                if self.direction.length() != 0:
                    self.player.direction = self.direction.normalize() * -7

    def animate(self):
        # Only use if in a shooting state
        if self.action != 'idle':
            self.frame_index += self.animation_speeds[self.action]

            if self.frame_index >= len(self.frames[self.action]):
                self.frame_index = 0
                self.action = 'idle'  # Back to static image

    def update(self):
        #Position and direction logic
        mouse_pos = pygame.mouse.get_pos()
        mouse_world = mouse_pos + self.player.groups()[0].offset
        self.direction = pygame.math.Vector2(mouse_world) - pygame.math.Vector2(self.player.rect.center)

        if self.direction.length() != 0:
            self.direction = self.direction.normalize()

        self.angle = math.degrees(math.atan2(self.direction.y, self.direction.x))
        weapon_pos = pygame.math.Vector2(self.player.rect.center) + self.direction * 40

        #Run animation logic
        self.animate()

        #Select the base image BEFORE rotating
        if self.action == 'idle':
            # Use static PNGs
            base_img = self.original_image
            flipped_base = self.flipped_image
        else:
            # Use current animation frame
            base_img = self.frames[self.action][int(self.frame_index)]
            flipped_base = pygame.transform.flip(base_img, False, True)

        #Rotate the correct base image (Animation frame or Static)
        if 90 > self.angle > -90:
            self.image = pygame.transform.rotate(base_img, -self.angle)
        else:
            self.image = pygame.transform.rotate(flipped_base, -self.angle)

        self.rect = self.image.get_rect(center=weapon_pos)
