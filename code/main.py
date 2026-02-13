import pygame
from settings import *
from level import Level


#General setup
pygame.init()
pygame.display.set_caption('Insolitum')

info = pygame.display.Info()
MONITOR_WIDTH = info.current_w
MONITOR_HEIGHT = info.current_h

#Start in fullscreen (Maybe replace NOFRAME with FULLFRAME later)
is_fullscreen = True
screen = pygame.display.set_mode(
    (MONITOR_WIDTH, MONITOR_HEIGHT), pygame.NOFRAME)

game_surface = pygame.Surface((BASE_SCREEN_WIDTH, BASE_SCREEN_HEIGHT))

clock = pygame.time.Clock()
dt = True
running = True
level = Level(game_surface)


#Main game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        #Toggle fullscreen with F11
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_F11:
                is_fullscreen = not is_fullscreen

                if is_fullscreen:
                    screen = pygame.display.set_mode((MONITOR_WIDTH, MONITOR_HEIGHT),pygame.NOFRAME)
                else:
                    screen = pygame.display.set_mode(
                        (BASE_SCREEN_WIDTH, BASE_SCREEN_HEIGHT),pygame.RESIZABLE)

        #Window resizing
        if event.type == pygame.VIDEORESIZE and not is_fullscreen:
            screen = pygame.display.set_mode((event.w, event.h),pygame.RESIZABLE)

    game_surface.fill((0, 0, 0))
    level.run()

    scaled_surface = pygame.transform.scale(game_surface, screen.get_size())

    screen.blit(scaled_surface, (0, 0))
    pygame.display.update()

    #Test to kill enemy (will be removed)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_l]:
        for sprite in level.visible_sprites:
            if hasattr(sprite, 'take_damage'):
                sprite.take_damage(1)

    dt = clock.tick(60) / 1000



pygame.quit()
