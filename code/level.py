import pygame
from settings import *
from tile import Tiles
from player import Player
from support import *
from flyingenemy import FlyingEnemy


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
            'surface': import_csv_layout('../levels/0/lvl_mvp_surface.csv'),
            'dirt': import_csv_layout('../levels/0/lvl_mvp_dirt.csv'),
            'bridge_side': import_csv_layout('../levels/0/lvl_mvp_bridge_side.csv'),
            'bridge_top': import_csv_layout('../levels/0/lvl_mvp_bridge_top.csv')
        }

        graphics = {
            'surface': import_folder('../graphics/deepcave_single_tiles/surface'),
            'dirt': import_folder('../graphics/deepcave_single_tiles/dirt'),
            'bridge_side': import_folder('../graphics/deepcave_single_tiles/bridge_side'),
            'bridge_top': import_folder('../graphics/deepcave_single_tiles/bridge_top'),
        }

        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILE_SIZE
                        y = row_index * TILE_SIZE

                        if style == 'surface':
                            surf = graphics['surface'][int(col)]
                            Tiles((x,y), [self.visible_sprites, self.obstacle_sprites], 'surface', surface=surf)
                        if style == 'dirt':
                            dirt = graphics['dirt'][int(col)]
                            Tiles((x,y), [self.visible_sprites, self.obstacle_sprites], 'dirt', surface=dirt)
                        if style == 'bridge_side':
                            b_side = graphics['bridge_side'][int(col)]
                            Tiles((x,y), [self.visible_sprites], 'bridge_side', surface=b_side)
                        if style == 'bridge_top':
                            b_top = graphics['bridge_top'][int(col)]
                            Tiles((x,y), [self.visible_sprites, self.obstacle_sprites], 'bridge_top', surface=b_top)

        self.player = Player((700, 500), [self.visible_sprites], self.obstacle_sprites)

        FlyingEnemy((900, 400), [self.visible_sprites], self.player, self.obstacle_sprites)

    # Render
    def run(self):
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()


class YSortCameraGroup(pygame.sprite.Group):

    def __init__(self):
        # General
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_screen_width = pygame.display.get_window_size()[0] // 2
        self.half_screen_height = pygame.display.get_window_size()[1] // 2
        self.offset = pygame.math.Vector2()

        #Loading a background (Temporary, needs to be a function)
        self.bg_layer_0 = pygame.image.load('../graphics/deepcave_background/DeepCaveBG-Base.png').convert()
        self.bg_layer_1 = pygame.image.load('../graphics/deepcave_background/DeepCaveBG-Layer1.png').convert_alpha()
        self.bg_layer_2 = pygame.image.load('../graphics/deepcave_background/DeepCaveBG-Layer2.png').convert_alpha()
        self.bg_layer_3 = pygame.image.load('../graphics/deepcave_background/DeepCaveBG-Layer3.png').convert_alpha()

        self.bg_layer_00 = pygame.transform.scale_by(self.bg_layer_0, 3)
        self.bg_layer_01 = pygame.transform.scale_by(self.bg_layer_1, 3)
        self.bg_layer_02 = pygame.transform.scale_by(self.bg_layer_2, 3)
        self.bg_layer_03 = pygame.transform.scale_by(self.bg_layer_3, 3)


    def draw_parallax_layer(self, image, factor):
        layer_width = image.get_width()
        layer_height = image.get_height()

        x = -self.offset.x * factor
        y = -self.offset.y * factor

        # Clamp horizontally
        max_x = layer_width - SCREEN_WIDTH
        x = max(-max_x, min(0, x))

        # Clamp vertically
        max_y = layer_height - SCREEN_HEIGHT
        y = max(-max_y, min(0, y))

        self.display_surface.blit(image, (x, y))


    def custom_draw(self, player):

        #Offset (camera)
        self.offset.x =player.rect.centerx - self.half_screen_width
        self.offset.x = max(0, min(self.offset.x, WORLD_WIDTH - SCREEN_WIDTH))
        self.offset.y = player.rect.centery - self.half_screen_height
        self.offset.y = max(0, min(self.offset.y, WORLD_HEIGHT - SCREEN_HEIGHT))

        # Parallax layers
        self.draw_parallax_layer(self.bg_layer_00, 1)
        self.draw_parallax_layer(self.bg_layer_01, 0.1)
        self.draw_parallax_layer(self.bg_layer_02, 0.3)
        self.draw_parallax_layer(self.bg_layer_03, 0.6)


        for sprite in self.sprites():
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

