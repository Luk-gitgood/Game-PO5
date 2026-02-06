import pygame
from settings import *
from tile import Tiles
from player import Player
from support import *
from enemy import Enemy


class Level:

    def __init__(self):

        #Get the display surface
        self.display_surface = pygame.display.get_surface()

        #Sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        #create map
        self.create_map()


    def create_map(self):
        layouts = {
            'map': import_csv_layout('levels/0/level_0_Tile_Layer 2.csv')
        }

        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILE_SIZE
                        y = row_index * TILE_SIZE
                        if style == 'map':
                            terrain_tile_list = import_cut_graphic('graphics/terrain/dungeon_bricks.png')
                            map_graphics = terrain_tile_list[int(col)]
                            Tiles((x,y), [self.visible_sprites, self.obstacle_sprites], 'map', surface=map_graphics)

        self.player = Player((700,200), [self.visible_sprites], self.obstacle_sprites)

        #placeholder enemy
        Enemy((700, 200), [self.visible_sprites], self.player, self.obstacle_sprites)
        
        

    #Render
    def run(self):
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()



class YSortCameraGroup(pygame.sprite.Group):

    def __init__(self):

        #General
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_screen_width = pygame.display.get_window_size()[0] // 2
        self.half_screen_height = pygame.display.get_window_size()[1] // 2
        self.offset = pygame.math.Vector2()

        #Loading a background
        self.background = pygame.image.load('graphics/terrain/test_lvl_0.png').convert()
        self.background_rect = self.background.get_rect(topleft=(-100,-100))

    def custom_draw(self, player):

        #Offset (camera)
        self.offset.x = player.rect.centerx - self.half_screen_width
        self.offset.y = player.rect.centery - self.half_screen_height

        #Moving the background
        offset_background = (self.background_rect.x - self.offset.x * 0.3, self.background_rect.y - self.offset.y * 0.3)
        self.display_surface.blit(self.background, offset_background)

        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

        # Draw healthbars for enemies
        for sprite in self.sprites():
            if hasattr(sprite, 'draw_health_bar'):
                sprite.draw_health_bar(self.display_surface, self.offset)