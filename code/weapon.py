import pygame

class Weapon(pygame.sprite.Sprite):

    def __init__(self, groups, player):
        super().__init__(groups)
        self.player = player

        self.image = pygame.image.load('../graphics/test_images/test_gun.png').convert_alpha()

        #Gun direction
        if self.player.facing_left:
            self.rect = self.image.get_rect(midright=self.player.hitbox.midleft)
        else:
            self.image = pygame.transform.flip(self.image, True, False)
            self.rect = self.image.get_rect(midleft=self.player.hitbox.midright)

