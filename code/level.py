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
    """
    Beheert de volledige spelwereld, inclusief het laden van de kaart, entiteiten en rendering.

    De Level-klasse is verantwoordelijk voor het interpreteren van CSV-layouts, 
    het spawnen van de speler en vijanden, en het coördineren van de interacties 
    tussen sprites (zoals wapens en collisions).

    Attributes:
        display_surface (pygame.Surface): De surface waarop het level getekend wordt.
        visible_sprites (YSortCameraGroup): Een speciale groep voor sprites die getekend moeten worden.
        obstacle_sprites (pygame.sprite.Group): Sprites waar entiteiten niet doorheen kunnen lopen.
        attackable_sprites (pygame.sprite.Group): Entiteiten die schade kunnen ontvangen (vijanden).
        player (Player): De speler-instantie.
        ui (UI): Het gebruikersinterface-systeem voor het level.
    """

    def __init__(self, surface):
        """
        Initialiseert het level, de sprite-groepen en de gebruikersinterface.

        Args:
            surface (pygame.Surface): De hoofd-surface van de game.
        """
        self.display_surface = surface

        # Sprite groepen
        self.visible_sprites = YSortCameraGroup(self.display_surface)
        self.obstacle_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()
    
        # Wapen beheer
        self.current_weapon = None
        self.weapon_destroyed_on_death = False

        # Parallax instelling
        self.use_parallax = False

        # Wereld aanmaken
        self.create_map()

        # Gebruikersinterface
        self.ui = UI(self.display_surface)

    def create_map(self):
        """
        Leest CSV-bestanden uit en plaatst tegels (tiles), decoraties en vijanden op de juiste posities.
        Initialiseert ook de speler op een vaste startpositie.
        """
        # Speler aanmaken (eerst, zodat vijanden een referentie hebben voor tracking)
        self.player = Player(
            (450, 1700),
            [self.visible_sprites],
            self.obstacle_sprites,
            self.equip_weapon,
            self.destroy_weapon,
            self.fire_weapon
        )

        layouts_path = BASE_DIR.parent / 'levels' / '1' / 'boss_room'

        # Definieer alle kaartlagen
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

        # Loop door alle lagen en tegels
        for style, layout in layouts.items():
            for row_index, row in enumerate(layout): 
                for col_index, col in enumerate(row): 

                    if col == '-1':
                        continue
                    x = col_index * TILE_SIZE
                    y = row_index * TILE_SIZE

                    # Vijand spawn laag (onzichtbaar)
                    if style == 'enemy_spawns':
                        enemy_type = ENEMY_TYPES.get(col)
                        if enemy_type is None:
                            continue

                        enemy_data = ENEMY_DATA[enemy_type]
                        enemy_class = enemy_data['class']

                        if enemy_class == 'walking': 
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
                        continue 

                    index = int(col)
                    if 0 <= index < len(graphics[style]):
                        surf = graphics[style][index]

                        # Bepaal het type tegel en de bijbehorende groepen/eigenschappen
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
                            print(f"Waarschuwing: '{style}' index {index} buiten bereik.")

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

    def run(self):
        """
        Update en rendert alle elementen in het level.
        Behandelt ook de 'Game Over' logica wanneer de speler sterft.
        """
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()
        self.ui.display(self.player)
        
        # Teken health bars voor aanvalbare vijanden
        for enemy in self.attackable_sprites:
            enemy.draw_health_bar(self.display_surface, self.visible_sprites.offset)

        # Game Over status
        if self.player.dead:
            if not self.weapon_destroyed_on_death:
                self.destroy_weapon()
                self.weapon_destroyed_on_death = True
            
            font = pygame.font.Font(None, 74)
            text = font.render("Game Over", True, (255, 255, 255))
            self.display_surface.blit(text, (BASE_SCREEN_WIDTH // 2 - text.get_width() // 2, BASE_SCREEN_HEIGHT // 2 - text.get_height() // 2))

class YSortCameraGroup(pygame.sprite.Group):
    """
    Een aangepaste sprite-groep die een camera-systeem en parallax-achtergronden beheert.

    Deze groep zorgt ervoor dat sprites worden getekend met een offset gebaseerd 
    op de positie van de speler, waardoor de speler altijd centraal in beeld blijft.
    """

    def __init__(self, surface):
        """
        Initialiseert de camera groep en laadt de achtergrondlagen voor parallax.

        Args:
            surface (pygame.Surface): De surface waarop de camera moet tekenen.
        """
        super().__init__()
        self.display_surface = surface
        self.half_screen_width = BASE_SCREEN_WIDTH // 2
        self.half_screen_height = BASE_SCREEN_HEIGHT // 2
        self.offset = pygame.math.Vector2()

        # Achtergronden laden
        bg_path = BASE_DIR.parent / 'graphics' / 'level_graphics' / 'castle_single_tiles' / 'background'
        self.bg_layer_0 = pygame.image.load(bg_path / 'DarkCaveBG-Base.png').convert()
        self.bg_layer_1 = pygame.image.load(bg_path / 'DarkCaveBG-Layer1.png').convert_alpha()
        self.bg_layer_2 = pygame.image.load(bg_path / 'DarkCaveBG-Layer2.png').convert_alpha()
        self.bg_layer_3 = pygame.image.load(bg_path / 'DarkCaveBG-Layer3.png').convert_alpha()
        self.bg_layer_4 = pygame.image.load(bg_path / 'DarkCaveBG-Layer4.png').convert_alpha()

        # Achtergronden schalen
        self.bg_layer_00 = pygame.transform.scale_by(self.bg_layer_0, 3)
        self.bg_layer_01 = pygame.transform.scale_by(self.bg_layer_1, 3)
        self.bg_layer_02 = pygame.transform.scale_by(self.bg_layer_2, 3)
        self.bg_layer_03 = pygame.transform.scale_by(self.bg_layer_3, 3)
        self.bg_layer_04 = pygame.transform.scale_by(self.bg_layer_4, 3)

    def draw_parallax_layer(self, image, factor):
        """
        Tekent een specifieke achtergrondlaag met een snelheidsfactor voor het parallax-effect.

        Args:
            image (pygame.Surface): De afbeelding van de laag.
            factor (float): De snelheid waarmee de laag beweegt t.o.v. de camera (0-1).
        """
        layer_width = image.get_width()
        layer_height = image.get_height()

        x = -self.offset.x * factor
        y = WORLD_HEIGHT - layer_height - self.offset.y - BOTTOM_LAYER

        # Horizontale begrenzing
        max_x = layer_width - BASE_SCREEN_WIDTH
        x = max(-max_x, min(0, x))

        self.display_surface.blit(image, (x, y))

    def custom_draw(self, player):
        """
        Berekent de camera-offset en tekent alle zichtbare sprites en achtergronden.

        Alleen sprites die zich binnen het schermkader bevinden worden getekend (culling).

        Args:
            player (Player): De speler-entiteit die de camera moet volgen.
        """
        # Camera offset berekenen en begrenzen binnen de wereld
        self.offset.x = player.rect.centerx - self.half_screen_width
        self.offset.x = max(0, min(self.offset.x, WORLD_WIDTH - BASE_SCREEN_WIDTH))
        self.offset.y = player.rect.centery - self.half_screen_height
        self.offset.y = max(0, min(self.offset.y, WORLD_HEIGHT - BASE_SCREEN_HEIGHT))

        render_offset_x = int(self.offset.x)
        render_offset_y = int(self.offset.y)

        # Achtergrondlagen tekenen
        if getattr(self, 'use_parallax', False):
            self.draw_parallax_layer(self.bg_layer_00, 1)
            self.draw_parallax_layer(self.bg_layer_01, 0.1)
            self.draw_parallax_layer(self.bg_layer_02, 0.3)
            self.draw_parallax_layer(self.bg_layer_03, 0.6)
            self.draw_parallax_layer(self.bg_layer_04, 0.9)
        else:
            self.display_surface.fill((15,15,0))

        # Sprites tekenen met culling (alleen wat op het scherm past)
        screen_rect = pygame.Rect(render_offset_x, render_offset_y, BASE_SCREEN_WIDTH, BASE_SCREEN_HEIGHT)

        for sprite in self.sprites():
            if screen_rect.colliderect(sprite.rect):
                draw_x = sprite.rect.left - render_offset_x
                draw_y = sprite.rect.top  - render_offset_y
                self.display_surface.blit(sprite.image, (draw_x, draw_y))