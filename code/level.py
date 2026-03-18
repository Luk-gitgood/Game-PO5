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
        #verkrijg display oppervlak
        self.display_surface = surface
        self.room = 'woods_room' #de eerste kamer waarin de game start (buitenwereld)
        self.spawn_pos = (550, 1150) #hardcoded spawnpos TODO maak gebasseerd op tile ID

        #Sprite group setup
        # visible sprite worden gemaakt in create_map aangezien deze world with en world height parameters nodig hebben

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
                    
        # selecteer de tileset dynamisch gebasseerd op naam van wereld (**BELANGRIJK**: benoem de tileset folders hetzelfde als de wereld folders)
        tileset_name = f"{self.room}_single_tiles"  
        graphics_path = BASE_DIR.parent / 'graphics' / 'level_graphics' / tileset_name

        #laad alle graphics met gebruik van import_folder functie uit support.py
        graphics = {  
            'collision_surface': import_folder(graphics_path / 'collision_surface'),
            'damage_tiles': import_folder(graphics_path / 'damage_tiles'),
            'background1': import_folder(graphics_path / 'non_collision_surface'),
            'platform_top': import_folder(graphics_path / 'platform_top'),
            'doorways': import_folder(graphics_path / 'doorways'),
            'decorations': import_folder(graphics_path / 'decorations'),
        }

        #map dimensies
        layout_reference = layouts['collision_surface']
        self.map_rows = len(layout_reference) 
        self.map_cols = len(layout_reference[0]) 

        self.world_height = self.map_rows * TILE_SIZE #bepaalt wereld grote gebasseerd op aantal rows in csv file
        self.world_width = self.map_cols * TILE_SIZE #bepaalt wereld width gebasseerd op aantal columns in csv file

        self.visible_sprites = YSortCameraGroup(
                self.display_surface,
                self.world_width,
                self.world_height  
            )

        #maak player voor alle andere sprites omdat enemies player als argument nodig hebben voor hun functies
        self.player = Player(
        self.spawn_pos,
        [self.visible_sprites],
        self.obstacle_sprites,
        self.equip_weapon,
        self.destroy_weapon,
        self.fire_weapon
        )


        #loop over alle styles (tile layers)
        for style, layout in layouts.items():
            for row_index, row in enumerate(layout): 
                for col_index, col in enumerate(row): 

                    if col == '-1': #als value in csv file -1, skip de loop aangezien -1 'geen tile' betekent in CSV
                        continue
                    x = col_index * TILE_SIZE
                    y = row_index * TILE_SIZE

                    #enemy spawn laag (no graphics)
                    if style == 'enemy_spawns':

                        enemy_type = ENEMY_TYPES.get(col) #verkrijg enemy_typ van de enemy_data dict
                        
                        if enemy_type is None: #als de waarde in het CSV file niet met een enemy type overeenkomt, skip
                            continue

                        enemy_data = ENEMY_DATA[enemy_type] #lees uit enemy_data file
                        enemy_class = enemy_data['class'] #krijg class of enemy van enemy_data.py

                        if enemy_class == 'walking': #als het een walking enemy is, spawn een walking enemy 
                            WalkingEnemy(
                                (x, y),
                                [self.visible_sprites, self.attackable_sprites],
                                self.player,
                                self.obstacle_sprites,
                                self.attackable_sprites,
                                enemy_type,
                                self.display_surface
                            )

                        elif enemy_class == 'flying': #dito
                            FlyingEnemy(
                                (x, y),
                                [self.visible_sprites, self.attackable_sprites],
                                self.player,
                                self.obstacle_sprites,
                                self.attackable_sprites,
                                enemy_type
                            )
                        continue #skip de rest van de loop, aangezien enemy spawning tiles niet zichtbaar zijn

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
        self.create_map() #maakt nieuwe map. Side effect is dat ook player nieuw word gemaakt met volledige health. Dit is duidelijk een feature en geen fout

    def start_transition(self, room, spawn_pos):
        self.fading = True
        self.fade_direction = 1
        self.next_room = room
        self.next_spawn = spawn_pos

    def handle_fade(self):
        if not self.fading: #alleen doorgaan als self.fading vlag true is
            return

        self.fade_alpha += self.fade_speed * self.fade_direction #zet fade_alpha snel op 255 (zwart scherm)

        # volledig zwart = laad nieuwe kamer
        if self.fade_alpha >= 255:
            self.fade_alpha = 255
            self.change_room(self.next_room, self.next_spawn)
            self.fade_direction = -1 #makes the fade_alpha go down again

        # fade klaar
        if self.fade_alpha <= 0: #wanneer fade = 0, laad de map
            self.fade_alpha = 0
            self.fading = False

        fade_surface = pygame.Surface((BASE_SCREEN_WIDTH, BASE_SCREEN_HEIGHT))
        fade_surface.fill((0,0,0))
        fade_surface.set_alpha(self.fade_alpha)

        self.display_surface.blit(fade_surface, (0,0))

    # Render en run alle functies
    def run(self):

        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()
        self.ui.display(self.player)

        for enemy in self.attackable_sprites:
            enemy.draw_health_bar(self.display_surface, self.visible_sprites.offset)

        self.handle_fade()

        for sprite in self.visible_sprites:
            if hasattr(sprite, "sprite_type") and sprite.sprite_type == "door": #checkt of een sprite een deur is, en als dat zo is start kamer transition
                if self.player.rect.colliderect(sprite.rect) and not self.fading:
                    if sprite.target_room:
                        self.start_transition(sprite.target_room, sprite.spawn_pos)

        if self.player.dead:
            if not self.weapon_destroyed_on_death: #zorgt dat wapen sprite ook verdwijnt op death
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