import pygame

class Weapon(pygame.sprite.Sprite):

    def __init__(self, groups, player):
        super().__init__(groups)
        self.player = player

        full_path = f'../graphics/test_images/{self.player.weapon}.png'
        self.image = pygame.image.load(full_path).convert_alpha()

        #Gun direction
        if self.player.facing_left:
            self.rect = self.image.get_rect(midright=self.player.hitbox.midleft)
        else:
            self.image = pygame.transform.flip(self.image, True, False)
            self.rect = self.image.get_rect(midleft=self.player.hitbox.midright)
