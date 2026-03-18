import pygame
from spritesheets import SpriteSheet
from entity import Entity
from settings import *
from random import uniform
from enemy_data import ENEMY_DATA

class FlyingEnemy(Entity):
    """
    Een vliegende vijand die de speler achtervolgt en aanvalt wanneer deze binnen bereik is.

    Deze class beheert de AI, animaties, collision-detectie en stats van vliegende 
    tegenstanders. De vijand kan door muren worden geblokkeerd, tenzij de logica 
    wordt aangepast voor volledige vrije vlucht.

    Attributes:
        enemy_type (str): Het type vijand (bijv. 'vleermuis'), gebruikt om data op te halen.
        stats (dict): Bevat gezondheid, schade, snelheid en detectieradius.
        player (pygame.sprite.Sprite): Referentie naar de speler voor tracking.
        obstacle_sprites (pygame.sprite.Group): Sprites die beweging blokkeren.
        player_detected (bool): Geeft aan of de vijand momenteel de speler achtervolgt.
        dying (bool): Statusvlag die aangeeft of de sterfanimaties worden afgespeeld.
    """

    def __init__(self, pos, groups, player, obstacle_sprites, attackable_sprites, enemy_type):
        """
        Initialiseert de FlyingEnemy met de benodigde parameters en laadt animaties.

        Args:
            pos (tuple): De (x, y) startpositie van de vijand.
            groups (list): De sprite-groepen waartoe deze vijand behoort.
            player (Entity): Het speler-object dat achtervolgd moet worden.
            obstacle_sprites (pygame.sprite.Group): Groep met ondoordringbare objecten.
            attackable_sprites (pygame.sprite.Group): Groep voor entiteiten die geraakt kunnen worden.
            enemy_type (str): Sleutel voor de ENEMY_DATA dictionary.
        """
        super().__init__(groups) 
        self.enemy_type = enemy_type
        self.data = ENEMY_DATA[self.enemy_type] #laad alle data van enemy_data.py
        self.stats = self.data['stats']

        # Animaties instellen
        graphics_path = BASE_DIR.parent / 'graphics' / 'character_animations' / self.data["path"]
        self.enemy_scale = self.data["scale"]
        self.animation_steps = self.data["animation_steps"]
        self.animation_speeds = self.data["animation_speeds"]

        # Laad frames direct in
        self.load_animation_frames(graphics_path)

        self.image = self.frames[self.action][0]
        self.rect = self.frames[self.action][0].get_rect(topleft = pos)
        self.player = player

        # Collision & Status
        self.obstacle_sprites = obstacle_sprites
        self.attackable_sprites = attackable_sprites
        self.hitbox = self.rect.inflate(0,0)
        self.dying = False

        # Enemy stats
        self.health = self.stats['health']
        self.damage = self.stats['damage']
        self.attack_cooldown = self.stats['attack_cooldown']
        self.last_attack_time = 0
        self.speed = uniform(*self.stats["speed"])

        # Speler detectie
        self.detection_radius = self.stats['detection_radius']
        self.disengage_radius = self.stats['disengage_radius']
        self.player_detected = False

    def load_animation_frames(self, graphics_path):
        """
        Laadt alle spritesheets in en verdeelt ze in individuele animatieframes.

        Args:
            graphics_path (Path): Het bestandspad naar de map met spritesheets. 
            file paths zijn belangrijk voor de code om te werken op verschillende machines
        """
        sheets = {}
        for key, value in self.data['sheets'].items():
            sheets[key] = SpriteSheet(pygame.image.load(graphics_path / value).convert_alpha())

        for action, sheet in sheets.items():
            self.frames[action] = [sheet.get_image(i, self.data['size']['width'], self.data['size']['height'], self.enemy_scale) for i in range(self.animation_steps[action])]

    def move_towards_player(self):
        """
        Berekent de richting naar de speler en verplaatst de vijand.
        normalisatie van de vector en collision-check.
        """
        self.direction.x = self.player.rect.centerx - self.rect.centerx
        self.direction.y = self.player.rect.centery - self.rect.centery

        if self.direction.length() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * self.speed
        self.check_collision('horizontal')

        self.hitbox.y += self.direction.y * self.speed
        self.check_collision('vertical')

        self.rect.center = self.hitbox.center

    def update_action(self):
        """
        Bepaalt welke animatie actie moet worden afgespeeld op basis van beweging en richting.
        """
        if self.dying:
            return

        if self.direction.length() == 0:
            self.action = 'idle'
        elif abs(self.direction.x) > abs(self.direction.y):
            self.action = 'fly_right'
            self.flip = self.direction.x < 0
        else:
            if 'fly_up' in self.animation_steps.keys():
                self.action = 'fly_up'

    def check_collision(self, direction):
        """
        Checkt op botsingen met obstakels en zet de positie terug indien nodig.

        Args:
            direction (str): 'horizontal' of 'vertical' om de specifieke as te controleren.
        """
        if direction == 'horizontal':
            for obstacle in self.obstacle_sprites:
                if obstacle.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0: self.hitbox.right = obstacle.hitbox.left
                    if self.direction.x < 0: self.hitbox.left = obstacle.hitbox.right

        if direction == 'vertical':
            for obstacle in self.obstacle_sprites:
                if obstacle.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:
                        self.hitbox.bottom = obstacle.hitbox.top
                        self.direction.y = 0
                    if self.direction.y < 0:
                        self.hitbox.top = obstacle.hitbox.bottom
                        self.direction.y = 0

    def detect_player(self):
        """
        Controleert of de speler binnen de detectieradius komt of de disengage-radius verlaat.
        Voorkomt eeuwige enemy leashing.
        """
        distance = pygame.math.Vector2(self.player.rect.center).distance_to(self.rect.center)
        if not self.player_detected:
            if distance <= self.detection_radius:
                self.player_detected = True
        else:
            if distance >= self.disengage_radius:
                self.player_detected = False
    
    def attack_player(self):
        """
        Voert een aanval uit op de speler als deze de hitbox raakt en de cooldown voorbij is.
        """
        current_time = pygame.time.get_ticks()

        if self.hitbox.colliderect(self.player.hitbox):
            if current_time - self.last_attack_time >= self.attack_cooldown:
                if 'attack' in self.animation_steps.keys():
                    self.action = 'attack'
                self.player.take_damage(self.damage)
                self.last_attack_time = current_time

    def can_see_player(self):
        """
        Gebruikt raycasting (clipline) om te zien of er een obstakel tussen de vijand en de speler staat.

        Returns:
            bool: True als er vrij zicht is, False als het zicht geblokkeerd is.
        """
        start = self.rect.center
        end = self.player.rect.center
    
        for obstacle in self.obstacle_sprites:
            if obstacle.sprite_type == 'platform_top':
                continue
            else:
                if obstacle.hitbox.clipline(start, end):
                    return False
        return True

    def take_damage(self, amount):
        """
        Vermindert de gezondheid van de vijand en start de 'hurt' of 'death' animatie.

        Args:
            amount (int): De hoeveelheid schade die de vijand oploopt.
        """
        if self.dying:
            return

        self.health -= amount
        if self.health <= 0:
            self.dying = True
            self.action = 'death'
            self.remove(self.attackable_sprites)
            self.frame_index = 0
            self.speed = 0
            return

        if 'hurt' in self.animation_steps.keys() and not self.dying:
            self.is_hurt = True
            self.action = 'hurt'
            self.frame_index = 0

    def draw_health_bar(self, surface, offset):
        """
        Tekent een gezondheidsbalk boven het hoofd van de vijand als deze schade heeft opgelopen.

        Args:
            surface (pygame.Surface): Het scherm of de surface waarop getekend moet worden.
            offset (pygame.math.Vector2): De camera-offset om de wereldpositie naar het scherm te vertalen.
        """
        if self.health >= self.stats['health']:
            return

        bar_x = self.rect.centerx - ENEMY_BAR_WIDTH // 2 - offset.x
        bar_y = self.rect.top - BAR_OFFSET_Y - offset.y

        bg_rect = pygame.Rect(bar_x, bar_y, ENEMY_BAR_WIDTH, ENEMY_BAR_HEIGHT)
        pygame.draw.rect(surface, UI_BG_COLOR, bg_rect)

        ratio = self.health / self.stats['health']
        current_rect = bg_rect.copy()
        current_rect.width = bg_rect.width * ratio

        pygame.draw.rect(surface, HEALTH_COLOR, current_rect)

    def update(self):
        """
        Update-loop voor de vijand: regelt detectie, beweging, aanvallen en animaties.
        """
        if not self.dying:
            self.detect_player()

            if self.player_detected and self.can_see_player():
                self.move_towards_player()
                self.attack_player()
            else:
                self.direction.update(0, 0)

            self.update_action()

        self.animate()