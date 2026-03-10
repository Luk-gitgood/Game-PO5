import pygame
from walkingenemy import WalkingEnemy
from tile import Tiles
from player import Player
from support import *
from flyingenemy import FlyingEnemy
from weapon import *
from settings import *
from ui import UI
from enemy_data import ENEMY_TYPES, ENEMY_DATA


class Level:

    def __init__(self,surface):
        #Get the display surface
        self.display_surface = surface

        #Sprite group setup
        self.visible_sprites = YSortCameraGroup(self.display_surface)
        self.obstacle_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()
    
        #Weapon
        self.current_weapon = None
        self.weapon_destroyed_on_death = False

        #parallax yes/no
        self.use_parallax = False

        #create map
        self.create_map()

        #user interface
        self.ui = UI(self.display_surface)

    def create_map(self):

        #create player first, as spawning enemies requires self.player as argument
        self.player = Player(
        (200, 2060),
        [self.visible_sprites],
        self.obstacle_sprites,
        self.equip_weapon,
        self.destroy_weapon,
        self.fire_weapon
        )

    
        layouts_path = BASE_DIR.parent / 'levels' /'1'/ 'boss_room'

        layouts = {
            'collision_surface': import_csv_layout(layouts_path / 'boss_room_collision_surface.csv'),
            'platform_top': import_csv_layout(layouts_path / 'boss_room_platform_top.csv'),
            'damage_tiles': import_csv_layout(layouts_path / 'boss_room_damage_tiles.csv'),
            'background1': import_csv_layout(layouts_path / 'boss_room_background1.csv'),
            'doorways': import_csv_layout(layouts_path / 'boss_room_doorways.csv'),
            'decorations': import_csv_layout(layouts_path / 'boss_room_decorations.csv'),
            'enemy_spawns': import_csv_layout(layouts_path / 'boss_room_enemy_spawns.csv'),
            }
        
        graphics_path = BASE_DIR.parent / 'graphics' / 'level_graphics' / 'castle_single_tiles'

        graphics = {
            'collision_surface': import_folder(graphics_path / 'collision_surface'),
            'damage_tiles': import_folder(graphics_path / 'damage_tiles'),
            'background1': import_folder(graphics_path / 'non_collision_surface'),
            'platform_top': import_folder(graphics_path / 'platform_top'),
            'doorways': import_folder(graphics_path / 'doorways'),
            'decorations': import_folder(graphics_path / 'decorations'),
        }

        #loop over all styles
        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):

                    if col == '-1':
                        continue
                    x = col_index * TILE_SIZE
                    y = row_index * TILE_SIZE

                    #enemy spawn layer (no graphics)
                    if style == 'enemy_spawns': 
                        if col in ENEMY_TYPES:
                            enemy_type = ENEMY_TYPES.get(col) #everywhere there is a 0 in the csv an enemy gets spawned
                            WalkingEnemy((x, y), 
                                [self.visible_sprites, self.attackable_sprites], 
                                self.player, 
                                self.obstacle_sprites, 
                                self.attackable_sprites,
                                'mushroom',
                                 ) 
                            continue

                    index = int(col)

                    if 0 <= index < len(graphics[style]):
                        surf = graphics[style][index]

                        if style == 'collision_surface':
                            Tiles((x, y), [self.visible_sprites, self.obstacle_sprites], 'solid', surf)

                        elif style == 'platform_top':
                            Tiles((x, y), [self.visible_sprites, self.obstacle_sprites], 'platform_top', surf)

                        elif style == 'damage_tiles':
                            Tiles((x, y), [self.visible_sprites, self.obstacle_sprites], 'damage', surf)

                        elif style == 'doorways':
                            Tiles((x, y), [self.visible_sprites], 'door', surf)

                        elif style == 'decorations':
                            Tiles((x, y), [self.visible_sprites], 'decoration', surf)

                        elif style == 'background1':
                            Tiles((x, y), [self.visible_sprites], 'surface', surf)
                                    
                                                                
                        else:
                            print(f"Warning: '{style}' index {index} out of range at row {row_index}, col {col_index}") #debugging thingy to check if the csv files are correct
                            print("collision_surface tiles:", len(graphics['collision_surface']))


    def equip_weapon(self):
        if self.current_weapon is None:
            self.current_weapon = Weapon([self.visible_sprites], self.player, self.obstacle_sprites, self.attackable_sprites, 40)

    def destroy_weapon(self):
        if self.current_weapon:
            self.current_weapon.kill()
            self.current_weapon = None

    def fire_weapon(self):
        #This checks if a weapon exists before trying to shoot
        if self.current_weapon:
            self.current_weapon.shoot()

    # Render
    def run(self):
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()
        self.ui.display(self.player)
        for enemy in self.attackable_sprites:
            enemy.draw_health_bar(self.display_surface, self.visible_sprites.offset)

        if self.player.dead:
            if not self.weapon_destroyed_on_death:
                self.destroy_weapon()
                self.weapon_destroyed_on_death = True
            font = pygame.font.Font(None, 74)
            text = font.render("Game Over", True, (255, 255, 255))
            self.display_surface.blit(text, (BASE_SCREEN_WIDTH // 2 - text.get_width() // 2, BASE_SCREEN_HEIGHT // 2 - text.get_height() // 2))

class YSortCameraGroup(pygame.sprite.Group):

    def __init__(self, surface):
        # General
        super().__init__()
        self.display_surface = surface
        self.half_screen_width = BASE_SCREEN_WIDTH // 2
        self.half_screen_height = BASE_SCREEN_HEIGHT // 2
        self.offset = pygame.math.Vector2()
        

        bg_path = BASE_DIR.parent / 'graphics' / 'level_graphics' /'castle_single_tiles' /'background'

        #Loading a background (Temporary, needs to be a function (maybe))
        self.bg_layer_0 = pygame.image.load(bg_path / 'DarkCaveBG-Base.png').convert()
        self.bg_layer_1 = pygame.image.load(bg_path / 'DarkCaveBG-Layer1.png').convert_alpha()
        self.bg_layer_2 = pygame.image.load(bg_path / 'DarkCaveBG-Layer2.png').convert_alpha()
        self.bg_layer_3 = pygame.image.load(bg_path / 'DarkCaveBG-Layer3.png').convert_alpha()
        self.bg_layer_4 = pygame.image.load(bg_path / 'DarkCaveBG-Layer4.png').convert_alpha()

        self.bg_layer_00 = pygame.transform.scale_by(self.bg_layer_0, 3)
        self.bg_layer_01 = pygame.transform.scale_by(self.bg_layer_1, 3)
        self.bg_layer_02 = pygame.transform.scale_by(self.bg_layer_2, 3)
        self.bg_layer_03 = pygame.transform.scale_by(self.bg_layer_3, 3)
        self.bg_layer_04 = pygame.transform.scale_by(self.bg_layer_4, 3)


    def draw_parallax_layer(self, image, factor):
        layer_width = image.get_width()
        layer_height = image.get_height()

        x = -self.offset.x * factor
        y = WORLD_HEIGHT - layer_height - self.offset.y - BOTTOM_LAYER

        #Clamp horizontally
        max_x = layer_width - BASE_SCREEN_WIDTH
        x = max(-max_x, min(0, x))

        self.display_surface.blit(image, (x, y))

    def custom_draw(self, player):

        #Offset (camera)
        self.offset.x = player.rect.centerx - self.half_screen_width
        self.offset.x = max(0, min(self.offset.x, WORLD_WIDTH - BASE_SCREEN_WIDTH))
        self.offset.y = player.rect.centery - self.half_screen_height
        self.offset.y = max(0, min(self.offset.y, WORLD_HEIGHT - BASE_SCREEN_HEIGHT))

        #Integer camera for rendering
        render_offset_x = int(self.offset.x)
        render_offset_y = int(self.offset.y)

        # Parallax layers
        if getattr(self, 'use_parallax', False):
            self.draw_parallax_layer(self.bg_layer_00, 1)
            self.draw_parallax_layer(self.bg_layer_01, 0.1)
            self.draw_parallax_layer(self.bg_layer_02, 0.3)
            self.draw_parallax_layer(self.bg_layer_03, 0.6)
            self.draw_parallax_layer(self.bg_layer_04, 0.9)
        else:
            self.display_surface.fill((15,15,0))

        for sprite in self.sprites():
            draw_x = sprite.rect.left - render_offset_x
            draw_y = sprite.rect.top  - render_offset_y
            self.display_surface.blit(sprite.image, (draw_x, draw_y))

            