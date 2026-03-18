import pygame
from .spritesheets import SpriteSheet
from .entity import Entity
from .settings import *
from random import uniform
from .enemy_data import ENEMY_DATA

class WalkingEnemy(Entity):
    """
    Representeert een vijand die de speler achtervolgt en aanvalt.
    
    Deze klasse gebruikt een state-machine (idle, walk, attack, hurt, death) 
    gecombineerd met raycasting-logica om te bepalen of de speler zichtbaar is.
    """

    def __init__(self, pos, groups, player, obstacle_sprites, attackable_sprites, enemy_type, surface):
        """
        Initialiseert de vijand op basis van data uit ENEMY_DATA.

        Args:
            pos (tuple): Startpositie (x, y).
            groups (list): Sprite-groepen.
            player (Player): Referentie naar het speler-object voor detectie en schade.
            obstacle_sprites (pygame.sprite.Group): Groep voor collision-detectie met muren/vloeren.
            attackable_sprites (pygame.sprite.Group): Groep voor vijanden die schade kunnen ontvangen.
            enemy_type (str): Key voor ENEMY_DATA om stats en animatiepaden op te halen.
        """
        super().__init__(groups)
        self.data = ENEMY_DATA[enemy_type]
        self.enemy_type = enemy_type
        self.stats = self.data['stats']
        self.player = player
        self.surface = surface

        graphics_path = BASE_DIR.parent / 'graphics' / 'character_animations' / self.data['path']
        self.enemy_scale = self.data['scale']
        self.animation_steps = self.data['animation_steps']
        self.animation_speeds = self.data['animation_speeds']

        self.load_animation_frames(graphics_path)

        self.image = self.frames[self.action][0]
        self.rect = self.frames[self.action][0].get_rect(topleft = pos)

        # Physics
        self.gravity = 0.4

        # Collision
        self.obstacle_sprites = obstacle_sprites
        self.attackable_sprites = attackable_sprites
        self.hitbox = self.rect.inflate(0,0)
        self.dying = False
        self.horizontal_collision = False
        self.damage_applied = False

        # State flags
        self.is_attacking = False
        self.is_hurt = False
        self.is_jumping = False
        self.on_ground = False

        # Enemy stats
        self.health = self.stats['health']
        self.damage = self.stats['damage']
        self.jump_height = self.stats['jump_height']
        self.attack_cooldown = self.stats['attack_cooldown']
        self.last_attack_time = 0
        self.speed = uniform(*self.stats['speed'])
        self.displayed_health = self.health

        # Player detection
        self.detection_radius = self.stats['detection_radius']
        self.disengage_radius = self.stats['disengage_radius']
        self.player_detected = False

        # Movement Variables
        self.accel = 0.4      
        self.friction = 0.2   
        self.max_speed = self.speed 
        self.direction.x = 0   
        self.look_ahead_dist = 30 

    def load_animation_frames(self, graphics_path):
        """
        Laadt alle spritesheets en knipt ze op in frames.

        De functie gebruikt de 'size' en 'animation_steps' uit ENEMY_DATA om 
        de correcte frames per actie (idle, walk, attack, etc.) te extraheren.
        """
        sheets = {}
        for key,value in self.data['sheets'].items():
            sheets[key] = SpriteSheet(pygame.image.load(graphics_path / value).convert_alpha())

        for action, sheet in sheets.items():
            self.frames[action] = [sheet.get_image(i, self.data['size']['width'], self.data['size']['height'], self.enemy_scale) for i in range(self.animation_steps[action])]

    def apply_gravity(self):
        """
        Past zwaartekracht toe op de vijand en controleert verticale botsingen.
        Zorgt ervoor dat de vijand op platforms blijft staan.
        """
        self.on_ground = False
        self.direction.y += self.gravity * 1.3
        self.hitbox.y += self.direction.y
        self.check_collision('vertical')
        self.rect.center = self.hitbox.center

    def move_towards_player(self):
        """
        Berekent de beweging richting de speler met acceleratie en wrijving.
        De vijand versnelt naar de x-positie van de speler en remt af bij stilstand.
        """
        if self.is_attacking:
            self.direction.x = 0
            return
    
        dx = self.player.rect.centerx - self.rect.centerx
        
        # Acceleratie logic
        if abs(dx) > 10:
            target_vel = 1 if dx > 0 else -1
            self.direction.x += target_vel * self.accel
        else:
            # Frictie logic
            if self.direction.x > 0:
                self.direction.x = max(0, self.direction.x - self.friction)
            elif self.direction.x < 0:
                self.direction.x = min(0, self.direction.x + self.friction)
    
        # Limiteer max speed
        if abs(self.direction.x) > 1: 
            self.direction.x = 1 if self.direction.x > 0 else -1
    
        self.jump()
    
        # Apply horizontal movement
        self.hitbox.x += self.direction.x * self.max_speed
        self.check_collision('horizontal')
        self.rect.center = self.hitbox.center

    def jump(self):
        """
        Voert een sprong uit als er een obstakel in de weg staat.
        
        Maakt een sensor rechthoek voor de vijand. Als deze een obstakel raakt 
        en de speler staat hoger, dan wordt de sprong geactiveerd.
        """
        if not self.on_ground: return

        look_dist = self.look_ahead_dist if self.direction.x >= 0 else -self.look_ahead_dist
        sensor_rect = self.hitbox.copy()
        sensor_rect.x += look_dist

        for obstacle in self.obstacle_sprites:
            if obstacle.hitbox.colliderect(sensor_rect):
                if self.player.rect.centery < self.rect.centery - 20:
                    self.direction.y = self.jump_height
                    self.on_ground = False
                    self.is_jumping = True #starts jump when player is higher
                    self.horizontal_collision = False
                    break

    def update_action(self):
        """
        Bepaalt de huidige animatie-state ('idle' of 'walk') op basis van snelheid.
        Stelt de flip-state in op basis van de looprichting
        """
        if self.dying or self.is_attacking or self.is_hurt:
            return 
    
        if abs(self.direction.x) < 0.1:
            self.action = 'idle'
            self.direction.x = 0 
        else:
            self.action = 'walk'
    
        if self.direction.x > 0: self.flip = False
        elif self.direction.x < 0: self.flip = True

    def check_collision(self, direction):
        """
        Handelt botsingen af met de omgevingssprites.
        Args:
            direction (str): 'horizontal' voor muren, 'vertical' voor vloeren.
        """
        if direction == 'horizontal':
            self.horizontal_collision = False
            for obstacle in self.obstacle_sprites:
                if obstacle.hitbox.colliderect(self.hitbox):
                    self.horizontal_collision = True
                    if self.direction.x > 0: self.hitbox.right = obstacle.hitbox.left
                    if self.direction.x < 0: self.hitbox.left = obstacle.hitbox.right

        if direction == 'vertical':
            for obstacle in self.obstacle_sprites:
                if obstacle.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:
                        self.hitbox.bottom = obstacle.hitbox.top
                        self.direction.y = 0
                        self.on_ground = True
                        self.is_jumping = False
                    if self.direction.y < 0:
                        self.hitbox.top = obstacle.hitbox.bottom
                        self.direction.y = 0

    def attack_player(self):
        """
        Beheert de timing van de aanval en voert schade uit op het juiste animatie-frame.
        Voorkomt dubbele schade door de 'damage_applied' vlag.
        """
        if self.is_hurt or self.dying:
            return
    
        current_time = pygame.time.get_ticks()
    
        if not self.is_attacking:
            if self.hitbox.colliderect(self.player.hitbox):
                if current_time - self.last_attack_time >= self.attack_cooldown:
                    self.is_attacking = True
                    self.action = 'attack'
                    self.frame_index = 0
                    self.damage_applied = False
                    self.last_attack_time = current_time
    
        if self.is_attacking and not self.damage_applied:
            if self.enemy_type =='hell_boss':
                if int(self.frame_index) == self.animation_steps['attack'] - 6:
                    if self.hitbox.colliderect(self.player.hitbox):
                        self.player.take_damage(self.damage)
                    self.damage_applied = True
            else:

                if int(self.frame_index) == self.animation_steps['attack'] - 2:
                    if self.hitbox.colliderect(self.player.hitbox):
                        self.player.take_damage(self.damage)
                    self.damage_applied = True

    def detect_player(self):
        """Bepaalt of de speler binnen het detectie- of disengage-bereik is."""
        distance = pygame.math.Vector2(self.player.rect.center).distance_to(self.rect.center) #distance_to bepaald afstand tussen 2 punten. zet deze in een vector
        if not self.player_detected:
            if distance <= self.detection_radius:
                self.player_detected = True
        else:
            if distance >= self.disengage_radius:
                self.player_detected = False

    def can_see_player(self):
        """
        Controleert Line of Sight met raycasting.
        
        Returnt False als er een muur tussen staat. (platformen worden geskipt)
        """
        start = self.rect.center
        end = self.player.rect.center
    
        for obstacle in self.obstacle_sprites:
            if obstacle.sprite_type == 'platform_top':
                continue
            else:
                if obstacle.hitbox.clipline(start, end): #checkt eigen locatie en player locatie met clipline
                    return False 
        return True

    def take_damage(self, amount):
        """
        Verwerkt inkomende damage. Bij health <= 0 start de 'death' animatie.
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
            self.player.kill_counter += 1
            return
        if not self.is_attacking:
            self.is_hurt = True
            self.action = 'hurt'
            self.frame_index = 0

    def draw_health_bar(self, surface, offset):
        if self.health >= self.stats['health']:
            return
    
        ratio = self.health / self.stats['health']
    
        if self.enemy_type == 'hell_boss':
            boss_width = 800 
            boss_height = 40
            bar_x = (surface.get_width() - boss_width) // 2
            bar_y = 60
    
            #Background
            bg_rect = pygame.Rect(bar_x, bar_y, boss_width, boss_height)
            pygame.draw.rect(surface, UI_BG_COLOR, bg_rect)
    
            #Lagging Bar
            self.displayed_health += (self.health - self.displayed_health) * 0.05 
            
            #Calculate width based on displayed_health
            white_width = int(boss_width * (self.displayed_health / self.stats['health']))
            white_rect = pygame.Rect(bar_x, bar_y, white_width, boss_height)
            pygame.draw.rect(surface, (255, 200, 200), white_rect)
    
            #Health Bar
            health_rect = pygame.Rect(bar_x, bar_y, int(boss_width * ratio), boss_height)
            pygame.draw.rect(surface, HEALTH_COLOR, health_rect)
    
        else:
            # Normale enemy bar logic
            bar_x = self.rect.centerx - ENEMY_BAR_WIDTH // 2 - offset.x
            bar_y = self.rect.top - BAR_OFFSET_Y - offset.y
            boss_width = ENEMY_BAR_WIDTH
            boss_height = ENEMY_BAR_HEIGHT

            # Draw background and health
            bg_rect = pygame.Rect(bar_x, bar_y, boss_width, boss_height)
            pygame.draw.rect(surface, UI_BG_COLOR, bg_rect)
            
            health_rect = bg_rect.copy()
            health_rect.width = int(bg_rect.width * ratio)
            pygame.draw.rect(surface, HEALTH_COLOR, health_rect)


    def update(self):
        """Hoofdfunctie: voert detectie, gedrag, fysica en animatie elke frame uit."""
        if self.dying:
            if self.enemy_type == 'hell_boss':
                victory_img = pygame.image.load(BASE_DIR.parent / 'graphics' / 'other_images' /'victory_screen.png').convert_alpha()
                victory_img = pygame.transform.scale(victory_img, (244, 100))

                screen_rect = self.surface.get_rect()
                victory_rect = victory_img.get_rect(center=screen_rect.center)

                self.surface.blit(victory_img, victory_rect)

                return

        if not self.dying:
            self.detect_player()
            if self.player_detected and self.can_see_player():
                if not self.is_attacking:
                    self.move_towards_player()
                self.attack_player()
            else:
                self.direction.x = 0
            self.apply_gravity()
            self.update_action()
        self.animate()