import pygame
from .settings import *

class Tiles(pygame.sprite.Sprite):
    """
    Representeert een individueel object of blok in de spelwereld.

    Deze klasse gebruikt een sprite-type om te bepalen hoe de speler met de tile 
    moet interageren (bijv. als vast object of als gevaarlijk element).

    Attributes:
        sprite_type (str): Het type object (bijv. 'surface', 'platform_top', 'damage').
        hitbox (pygame.Rect): De collision-zone die kleiner of groter kan zijn dan de visuele sprite.
    """


    def __init__(self, pos, groups, sprite_type, surface=pygame.Surface((TILE_SIZE, TILE_SIZE)), target_room = None, spawn_pos = None):
        """
        Initialiseert de tile op de kaart.

        Args:
            pos (tuple): De positie (x, y) op het scherm.
            groups (list): Groepen waaraan de sprite moet worden toegevoegd.
            sprite_type (str): Bepaalt de fysieke eigenschappen van de tile.
            surface (pygame.Surface, optional): De visuele afbeelding van de tile. 
                                                Standaard een leeg vierkant.
        """
        super().__init__(groups)
        self.sprite_type = sprite_type
        self.target_room = target_room
        self.spawn_pos = spawn_pos
        self.image = surface
        self.rect = self.image.get_rect(topleft=pos)

        # Bepaal de hitbox op basis van het type object. 
        # Inflate(x, y) past de afmetingen aan (positief vergroot, negatief verkleint).
        if self.sprite_type == 'surface':
            # Vaste muren/grond
            self.hitbox = self.rect.inflate(0, 0)

        elif self.sprite_type == 'platform_top':
            # One-way platforms waar je op kunt landen
            self.hitbox = self.rect.inflate(0, 0)
        
        elif self.sprite_type == 'damage':
            # Gevaarlijke objecten (zoals spikes). 
            # De hitbox wordt verkleind (-10 breedte, -30 hoogte) om het 
            # "hit-oppervlak" voor de speler te verfijnen.
            self.hitbox = self.rect.inflate(-10, -30)

        else:
            # Standaard: hitbox is gelijk aan de visuele rect
            self.hitbox = self.rect