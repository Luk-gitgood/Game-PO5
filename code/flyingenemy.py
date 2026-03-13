import pygame
from spritesheets import SpriteSheet
from entity import Entity
from settings import *
from random import uniform
from enemy_data import ENEMY_DATA



class FlyingEnemy(Entity):

    def __init__(self, pos, groups, player, obstacle_sprites, attackable_sprites, enemy_type):
        super().__init__(groups) 
        self.enemy_type = enemy_type
        self.data = ENEMY_DATA[self.enemy_type]
        self.stats = self.data['stats']

        # Animations
        graphics_path = BASE_DIR.parent / 'graphics' / 'character_animations' / self.data["path"]

        self.enemy_scale = self.data["scale"]
        self.animation_steps = self.data["animation_steps"]  # amount of frames in each animation
        self.animation_speeds = self.data["animation_speeds"]

        # Load frames immediately
        self.load_animation_frames(graphics_path)

        self.image = self.frames[self.action][0]
        self.rect = self.frames[self.action][0].get_rect(topleft = pos)
        self.player = player


        # collision
        self.obstacle_sprites = obstacle_sprites
        self.attackable_sprites = attackable_sprites
        self.hitbox = self.rect.inflate(0,0)
        self.dying = False

        #enemy stats
        self.health = self.stats['health']
        self.damage = self.stats['damage']
        self.attack_cooldown = self.stats['attack_cooldown']
        self.last_attack_time = 0
        self.speed = uniform(*self.stats["speed"]) #this makes the speed randomized between 2&3 to prevent enemies from getting stuck in eachother

        #player detection
        self.detection_radius = self.stats['detection_radius']
        self.disengage_radius = self.stats['disengage_radius']
        self.player_detected = False


    def load_animation_frames(self, graphics_path):
        #preload all animations
        sheets = {}
        for key,value in self.data['sheets'].items():
            sheets[key] = SpriteSheet(pygame.image.load(graphics_path / value).convert_alpha())

        for action, sheet in sheets.items():
            self.frames[action] = [sheet.get_image(i, self.data['size']['width'], self.data['size']['height'], self.enemy_scale) for i in range(self.animation_steps[action])]

    def move_towards_player(self):
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
        if self.dying:
            return

        if self.direction.length() == 0:
            self.action = 'idle'
        elif abs(self.direction.x) > abs(self.direction.y):
            if self.direction.x < 0:
                self.action = 'fly_left'
            else:
                self.action = 'fly_right'
        else:
            self.action = 'fly_up'

    def check_collision(self, direction):
        if direction == 'horizontal':
            for obstacle in self.obstacle_sprites:
                if obstacle.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:  # moving right
                        self.hitbox.right = obstacle.hitbox.left
                    if self.direction.x < 0:  # moving left
                        self.hitbox.left = obstacle.hitbox.right

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
        distance = pygame.math.Vector2(self.player.rect.center).distance_to(self.rect.center)
        if not self.player_detected:
            if distance <= self.detection_radius:
                self.player_detected = True
        else:
            if distance >= self.disengage_radius:
                self.player_detected = False
    
    def attack_player(self):
        current_time = pygame.time.get_ticks()

        if self.hitbox.colliderect(self.player.hitbox):
            if current_time - self.last_attack_time >= self.attack_cooldown:
                self.player.take_damage(self.damage)
                self.last_attack_time = current_time

    def take_damage(self, amount):
        if self.dying:
            return

        self.health -= amount
        if self.health <= 0:
            self.dying = True
            self.action = 'death'
            self.remove(self.attackable_sprites)
            self.frame_index = 0
            self.speed = 0

    def draw_health_bar(self,surface,offset):
        if self.health >= self.stats['health']:
            return

        #Convert world position to screen position
        bar_x = self.rect.centerx - ENEMY_BAR_WIDTH // 2 - offset.x
        bar_y = self.rect.top - BAR_OFFSET_Y - offset.y

        #Bg bar
        bg_rect = pygame.Rect(bar_x, bar_y, ENEMY_BAR_WIDTH, ENEMY_BAR_HEIGHT)
        pygame.draw.rect(surface, UI_BG_COLOR, bg_rect)

        #converting stats to pixels
        ratio = self.health / self.stats['health']
        current_width = bg_rect.width * ratio
        current_rect = bg_rect.copy()
        current_rect.width = current_width

        #drawng bar
        pygame.draw.rect(surface, HEALTH_COLOR, current_rect)

    def update(self):
        if not self.dying:
            self.detect_player()

            if self.player_detected:
                self.move_towards_player()
                self.attack_player()
            else:
                self.direction.update(0, 0)

            self.update_action()

        self.animate()
