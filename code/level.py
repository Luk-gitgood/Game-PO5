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

        #parallax yes/no (temporary, will probably be a setting in the future)
        self.use_parallax = False

        #create map
        self.create_map()

        #user interface
        self.ui = UI(self.display_surface)

    def create_map(self):

        #create player first, as spawning enemies requires self.player as argument, so that they can track the player
        self.player = Player(
        (450, 1700),
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
        
        graphics_path = BASE_DIR.parent / 'graphics' / 'level_graphics' / 'castle_single_tiles' #path to folder, so it runs on different machines / operating systems without needing to change the path in the code

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

                    if col == '-1': #if the value in the CSV is -1, skip the loop because -1 in CSV means there is no tile there
                        continue
                    x = col_index * TILE_SIZE
                    y = row_index * TILE_SIZE

                    #enemy spawn layer (no graphics)
                    if style == 'enemy_spawns':

                        enemy_type = ENEMY_TYPES.get(col) #get enemy type from ENEMY_TYPES dictionary using the value in the CSV
                        
                        if enemy_type is None: #if the value in the CSV doesn't correspond to an enemy type, skip it
                            continue

                        enemy_data = ENEMY_DATA[enemy_type] #read out enemy data file
                        enemy_class = enemy_data['class'] #get class of enemy from enemy_data.py

                        if enemy_class == 'walking': #if it's a walking enemy, spawn a walking enemy 
                            WalkingEnemy(
                                (x, y),
                                [self.visible_sprites, self.attackable_sprites],
                                self.player,
                                self.obstacle_sprites,
                                self.attackable_sprites,
                                enemy_type
                            )

                        elif enemy_class == 'flying':
                            FlyingEnemy(
                                (x, y),
                                [self.visible_sprites, self.attackable_sprites],
                                self.player,
                                self.obstacle_sprites,
                                self.attackable_sprites,
                                enemy_type
                            )
                        continue #skip the rest of the loop for enemy spawns, as the tiles dont need to be visible

                    index = int(col) #convert the value from the CSV to an integer to use as index for the graphics list for this style

                    if 0 <= index < len(graphics[style]): #check if the index is within the range of the graphics list for this style
                        surf = graphics[style][index] #get correct tile surface from graphics dictionary using the index from the CSV

                        if style == 'collision_surface': #collision tiles are solid and visible, so they go in both the visible_sprites and obstacle_sprites groups
                            Tiles((x, y), [self.visible_sprites, self.obstacle_sprites], 'solid', surf)

                        elif style == 'platform_top':
                            Tiles((x, y), [self.visible_sprites, self.obstacle_sprites], 'platform_top', surf)

                        elif style == 'damage_tiles': #just like collision surface but in different group so that they can have different properties (damaging the player)
                            Tiles((x, y), [self.visible_sprites, self.obstacle_sprites], 'damage', surf)

                        elif style == 'doorways': #only visible, but not in same layer as deco, to be able to give them different properties (like blocking the player)
                            Tiles((x, y), [self.visible_sprites], 'door', surf)

                        elif style == 'decorations': #only visible, no collisions
                            Tiles((x, y), [self.visible_sprites], 'decoration', surf)

                        elif style == 'background1':  #just background, no collisions, different layer so that it can be rendered behind the player and enemies
                            Tiles((x, y), [self.visible_sprites], 'surface', surf)
                                    
                                                                
                        else:
                            print(f"Warning: '{style}' index {index} out of range at row {row_index}, col {col_index}") #debugging thingy to check if the csv files are correct
                            print("collision_surface tiles:", len(graphics['collision_surface']))


    def equip_weapon(self, weapon_type):
        if self.current_weapon is None:
            self.current_weapon = Weapon([self.visible_sprites], self.player, self.obstacle_sprites, self.attackable_sprites, 40, weapon_type)

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

            