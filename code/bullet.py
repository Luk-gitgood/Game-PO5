import pygame
import math
from settings import *


class Bullet(pygame.sprite.Sprite):
    """
    Een kogel die beweegt, botsingen controleert en schade kan toebrengen.
    """

    def __init__(self, pos, angle, groups, obstacle_sprites, attackable_sprites, speed, lifetime, damage):
        """
        Maakt een nieuwe kogel aan.
        
        pos : tuple
            Startpositie van de kogel.
        angle : float
            Richting waarin de kogel wordt afgevuurd (in graden).
        groups : list
            Spritegroepen waarin de kogel wordt geplaatst.
        obstacle_sprites : list
            Sprites waartegen de kogel kan botsen.
        attackable_sprites : list
            Sprites die schade kunnen ontvangen.
        speed : float
            Snelheid van de kogel.
        lifetime : int
            Hoe lang de kogel blijft bestaan (in milliseconden).
        damage : int
            Hoeveel schade de kogel doet.
        """
        super().__init__(groups)

        # graphics
        self.image = pygame.Surface((12, 6), pygame.SRCALPHA)

        pygame.draw.ellipse(self.image, (255, 100, 0), [0, 0, 12, 6])
        pygame.draw.ellipse(self.image, (255, 255, 150), [2, 1, 8, 4])

        self.image = pygame.transform.rotate(self.image, -angle)

        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(pos)
        self.obstacle_sprites = obstacle_sprites
        self.attackable_sprites = attackable_sprites

        # movement
        rad = math.radians(angle)
        self.direction = pygame.math.Vector2(math.cos(rad), math.sin(rad))
        self.speed = speed

        # levensduur
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = lifetime

        # schade
        self.damage = damage

    def check_collision(self):
        """
        Controleert botsing met obstakels.
        """
        for sprite in self.obstacle_sprites:
            if sprite.hitbox.colliderect(self.rect):
                self.kill()

    def deal_damage(self):
        """
        Brengt schade toe aan aanvalbare sprites.
        """
        for sprite in self.attackable_sprites:
            if sprite.hitbox.colliderect(self.rect):
                sprite.take_damage(self.damage)
                self.kill()

    def update(self):
        """
        Beweegt de kogel, controleert botsingen en verwijdert hem na verloop van tijd.
        """
        self.pos += self.direction * self.speed
        self.rect.center = self.pos

        self.check_collision()
        self.deal_damage()

        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()