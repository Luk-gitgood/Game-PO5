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

    def __init__(self, surface):
        #Get the display surface
        self.display_surface = surface
        self.room = 'woods_room' #start room is the boss room for testing, but will be the outside world
        self.spawn_pos = (550, 1150)

        #Sprite group setup
        #   **visible sprites are created in create_map()**

        self.obstacle_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()
        
        #Weapon
        self.current_weapon = None
        self.weapon_destroyed_on_death = False

        #create map
        self.create_map()

        #user interface
        self.ui = UI(self.display_surface)

        #transition variables
        self.fade_alpha = 0
        self.fading = False
        self.fade_speed = 15
        self.fade_direction = 1  # 1 = fade out, -1 = fade in

        self.next_room = None
        self.next_spawn = None

    def create_map(self):

          #clear previous room
        if hasattr(self, "visible_sprites"):
            self.visible_sprites.empty()
        self.obstacle_sprites.empty()
        self.attackable_sprites.empty()

        layouts_path = BASE_DIR.parent / 'levels' / '1' / self.room

        layouts = {
            'collision_surface': import_csv_layout(layouts_path / f'{self.room}_collision_surface.csv'),
            'platform_top': import_csv_layout(layouts_path / f'{self.room}_platform_top.csv'),
            'damage_tiles': import_csv_layout(layouts_path / f'{self.room}_damage_tiles.csv'),
            'background1': import_csv_layout(layouts_path / f'{self.room}_background1.csv'),
            'doorways': import_csv_layout(layouts_path / f'{self.room}_doorways.csv'),
            'decorations': import_csv_layout(layouts_path / f'{self.room}_decorations.csv'),
            'enemy_spawns': import_csv_layout(layouts_path / f'{self.room}_enemy_spawns.csv'),
        }
                    
        # Dynamically select tileset folder based on room or world
        tileset_name = f"{self.room}_single_tiles"  # or self.world + "_" + self.room
        graphics_path = BASE_DIR.parent / 'graphics' / 'level_graphics' / tileset_name

        
        graphics = {  
            'collision_surface': import_folder(graphics_path / 'collision_surface'),
            'damage_tiles': import_folder(graphics_path / 'damage_tiles'),
            'background1': import_folder(graphics_path / 'non_collision_surface'),
            'platform_top': import_folder(graphics_path / 'platform_top'),
            'doorways': import_folder(graphics_path / 'doorways'),
            'decorations': import_folder(graphics_path / 'decorations'),
        }

        #map size
        layout_reference = layouts['collision_surface']
        self.map_rows = len(layout_reference) 
        self.map_cols = len(layout_reference[0]) 

        self.world_height = self.map_rows * TILE_SIZE #determines world height based on amount of rows in tilemap
        self.world_width = self.map_cols * TILE_SIZE #determines world width (dont have to hardcode it in settings anymore)

        self.visible_sprites = YSortCameraGroup(
                self.display_surface,
                self.world_width,
                self.world_height  
            )

        #create player before everything else, as spawning enemies requires self.player as argument, so that they can track the player
        self.player = Player(
        self.spawn_pos,
        [self.visible_sprites],
        self.obstacle_sprites,
        self.equip_weapon,
        self.destroy_weapon,
        self.fire_weapon
        )


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

                        elif style == 'doorways':
                            door_info = DOOR_DATA.get(col)

                            if door_info:
                                Tiles(
                                    (x, y),
                                    [self.visible_sprites],
                                    'door',
                                    surf,
                                    target_room=door_info["target_room"],
                                    spawn_pos=door_info["spawn_pos"]
                                ) #spawns the player at sewers room when walking over a door. Should be changed to be dynamic

                        elif style == 'decorations': #only visible, no collisions
                            Tiles((x, y), [self.visible_sprites], 'decoration', surf)

                        elif style == 'background1':  #just background, no collisions, different layer so that it can be rendered behind the player and enemies
                            Tiles((x, y), [self.visible_sprites], 'surface', surf)
                                    
                                                                
                        else:
                            print(f"Warning: '{style}' index {index} out of range at row {row_index}, col {col_index}") #debugging thingy to check if the csv files are correct, to be removed soon
                            print("collision_surface tiles:", len(graphics['collision_surface']))


    def equip_weapon(self, weapon_type):
        """
        Maakt een nieuw wapen aan voor de speler.

        Args:
            weapon_type (str): Het type wapen dat aangemaakt moet worden.
        """
        if self.current_weapon is None:
            self.current_weapon = Weapon([self.visible_sprites], self.player, self.obstacle_sprites, self.attackable_sprites, 40, weapon_type)

    def destroy_weapon(self):
        """Verwijdert het huidige wapen uit de game-wereld."""
        if self.current_weapon:
            self.current_weapon.kill()
            self.current_weapon = None

    def fire_weapon(self):
        """Activeert de schiet-functionaliteit van het huidige wapen."""
        if self.current_weapon:
            self.current_weapon.shoot()
            
    def change_room(self,room, spawn_pos):
        #let load the new level
        self.room = room
        self.spawn_pos = spawn_pos
        self.create_map()

    def start_transition(self, room, spawn_pos):
        self.fading = True
        self.fade_direction = 1
        self.next_room = room
        self.next_spawn = spawn_pos

    def handle_fade(self):
        if not self.fading: #only continue if transition fade has started
            return

        self.fade_alpha += self.fade_speed * self.fade_direction #makes fade_alpha quickly go to 255

        # fully black = change room
        if self.fade_alpha >= 255:
            self.fade_alpha = 255
            self.change_room(self.next_room, self.next_spawn)
            self.fade_direction = -1 #makes the fade_alpha go down again

        # fade finished
        if self.fade_alpha <= 0: #if fade = 0, load the map
            self.fade_alpha = 0
            self.fading = False

        fade_surface = pygame.Surface((BASE_SCREEN_WIDTH, BASE_SCREEN_HEIGHT))
        fade_surface.fill((0,0,0))
        fade_surface.set_alpha(self.fade_alpha)

        self.display_surface.blit(fade_surface, (0,0))

    # Render
    def run(self):

        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()
        self.ui.display(self.player)

        for enemy in self.attackable_sprites:
            enemy.draw_health_bar(self.display_surface, self.visible_sprites.offset)

        self.handle_fade()

        for sprite in self.visible_sprites:
            if hasattr(sprite, "sprite_type") and sprite.sprite_type == "door": #checks if a sprite is a door, and if so starts transition function
                if self.player.rect.colliderect(sprite.rect) and not self.fading:
                    if sprite.target_room:
                        self.start_transition(sprite.target_room, sprite.spawn_pos)

        if self.player.dead:
            if not self.weapon_destroyed_on_death:
                self.destroy_weapon()
                self.weapon_destroyed_on_death = True
            font = pygame.font.Font(None, 74)
            text = font.render("Game Over", True, (255, 255, 255))
            self.display_surface.blit(text, (BASE_SCREEN_WIDTH // 2 - text.get_width() // 2, BASE_SCREEN_HEIGHT // 2 - text.get_height() // 2))

class YSortCameraGroup(pygame.sprite.Group):

    def __init__(self, surface, world_width, world_height):

        # General
        super().__init__()
        self.display_surface = surface
        self.half_screen_width = BASE_SCREEN_WIDTH // 2
        self.half_screen_height = BASE_SCREEN_HEIGHT // 2
        self.offset = pygame.math.Vector2()

        self.world_width = world_width
        self.world_height = world_height
        

        bg_path = BASE_DIR.parent / 'graphics' / 'level_graphics' /'boss_room_single_tiles' /'background'

        


    def custom_draw(self, player):
        #calculates camera offset based on player position, but clamps it to the world boundaries so that it doesn't show anything outside of the map (which would look weird)
        self.offset.x = max(0, min(player.rect.centerx - self.half_screen_width, self.world_width - BASE_SCREEN_WIDTH))
        self.offset.y = max(0, min(player.rect.centery - self.half_screen_height, self.world_height - BASE_SCREEN_HEIGHT))

        render_offset_x = int(self.offset.x)
        render_offset_y = int(self.offset.y)

        #define the visible screen rect in world coordinates, so game can check whats in the players screen and only blit that (culling)
        screen_rect = pygame.Rect(render_offset_x, render_offset_y, BASE_SCREEN_WIDTH, BASE_SCREEN_HEIGHT)

        self.display_surface.fill((15, 15, 0))

        for sprite in self.sprites():
            if screen_rect.colliderect(sprite.rect):  #only blit what's visible (increases performance by a lot)
                draw_x = sprite.rect.left - render_offset_x
                draw_y = sprite.rect.top - render_offset_y
                self.display_surface.blit(sprite.image, (draw_x, draw_y))