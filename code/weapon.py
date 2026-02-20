import pygame
import math
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

        full_path = f"{graphics_path}/{self.player.weapon}.png"
        self.original_image = pygame.image.load(full_path).convert_alpha()
        self.flipped_image = pygame.transform.flip(self.original_image, False, True)
        self.image = self.original_image

        self.angle = None
        self.direction = None
        self.rect = self.image.get_rect(center=self.player.rect.center) #sets the weapon spawn on the player instead of (0,0)

    def shoot(self):
        # Get stats from your weapon_data dictionary in settings.py
        # Example: weapon_data = {'pistol': {'bullet_count': 1, 'spread': 0, 'speed': 15}...}
        weapon_stats = weapon_data[self.player.weapon]

        for _ in range(weapon_stats['bullet_count']):
            # Calculate spread
            spread = random.uniform(-weapon_stats['spread'], weapon_stats['spread'])
            shot_angle = self.angle + spread

            Bullet(
                self.rect.center,
                shot_angle,
                self.groups,
                self.obstacle_sprites,
                weapon_stats['speed'],
                weapon_stats['lifetime']
            )

        if self.player.weapon == 'Shotgun-1':
            if self.direction.length() != 0:  # prevents division by 0 while normalizing
                self.direction = self.direction.normalize()
            self.player.direction = self.direction * -7


    def update(self):

        #turn screen coordinates into world coordinates
        mouse_pos = pygame.mouse.get_pos()
        mouse_world = mouse_pos + self.player.groups()[0].offset

        #makes a vector from player center to the mouse
        self.direction = pygame.math.Vector2(mouse_world) - pygame.math.Vector2(self.player.rect.center)
        if self.direction.length() != 0: #prevents division by 0 while normalizing
            self.direction = self.direction.normalize() #sets vector length to 1

        #sets the position of weapon to a set offset in the direction of the mouse
        weapon_pos = pygame.math.Vector2(self.player.rect.center) + self.direction * 40

        #decides the relative angle between player and cursor
        self.angle = math.degrees(math.atan2(self.direction.y, self.direction.x))

        #turns the image to face the cursor AND flips the y-axis
        if 90 > self. angle > -90:
            self.image = pygame.transform.rotate(self.original_image, -self.angle)
        else:
            self.image = pygame.transform.rotate(self.flipped_image, -self.angle)

        #updates the position to prevent desync
        self.rect = self.image.get_rect(center=weapon_pos)
