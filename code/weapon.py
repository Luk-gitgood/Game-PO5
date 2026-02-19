import pygame
import math

class Weapon(pygame.sprite.Sprite):
    def __init__(self, wep_type, groups, player):
        super().__init__(groups)
        self.original_image = pygame.image.load(f"../graphics/test_images/{wep_type}.png")
        self.image = self.original_image

        self.groups = groups
        self.player = player
        self.wep_type = wep_type
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
        angle = math.degrees(math.atan2(direction.y, direction.x))

        #turns the image to face the cursor
        self.image = pygame.transform.rotate(self.original_image, -angle)
        #updates the position to prevent desync
        self.rect = self.image.get_rect(center=weapon_pos)
