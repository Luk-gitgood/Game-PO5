import pygame
from settings import *
from level import Level


#General setup
pygame.init()
pygame.display.set_caption('RogueTypeShit')
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
dt = True
running = True
level = Level()


#Main game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    level.run()
    pygame.display.update()
    keys = pygame.key.get_pressed()
    if keys[pygame.K_l]:
        for sprite in level.visible_sprites:
            if hasattr(sprite, 'take_damage'):
                sprite.take_damage(1)

    dt = clock.tick(60) / 1000


pygame.quit()
