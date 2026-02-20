import pygame
import math
from settings import *

class Weapon(pygame.sprite.Sprite):
    def __init__(self, groups, player):
        super().__init__(groups)

        graphics_path = BASE_DIR.parent / 'graphics' / 'weapons'

        self.groups = groups
        self.player = player

        full_path = f"{graphics_path}/{self.player.weapon}.png"
        self.original_image = pygame.image.load(full_path).convert_alpha()
        self.flipped_image = pygame.transform.flip(self.original_image, False, True)
        self.image = self.original_image

        self.angle = None
        self.rect = self.image.get_rect(center=self.player.rect.center) #sets the weapon spawn on the player instead of (0,0)


    def update(self):

        #turn screen coordinates into world coordinates
        mouse_pos = pygame.mouse.get_pos()
        mouse_world = mouse_pos + self.player.groups()[0].offset

        #makes a vector from player center to the mouse
        direction = pygame.math.Vector2(mouse_world) - pygame.math.Vector2(self.player.rect.center)
        if direction.length() != 0: #prevents division by 0 while normalizing
            direction = direction.normalize() #sets vector length to 1

        #sets the position of weapon to a set offset in the direction of the mouse
        weapon_pos = pygame.math.Vector2(self.player.rect.center) + direction * 40

        #decides the relative angle between player and cursor
        self.angle = math.degrees(math.atan2(direction.y, direction.x))

        #turns the image to face the cursor AND flips the y-axis
        if 90 > self. angle > -90:
            self.image = pygame.transform.rotate(self.original_image, -self.angle)
        else:
            self.image = pygame.transform.rotate(self.flipped_image, -self.angle)

        #updates the position to prevent desync
        self.rect = self.image.get_rect(center=weapon_pos)
