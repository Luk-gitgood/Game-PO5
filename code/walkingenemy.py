import pygame
from spritesheets import SpriteSheet
from entity import Entity
from settings import *
from random import uniform


class Walkingenemy(Entity):

    def __init__(self, pos, groups, player, obstacle_sprites, attackable_sprites):
        super().__init__(groups)

        # Animations
        graphics_path = BASE_DIR.parent / 'graphics' / 'character_animations' / 'igor'
        self.enemy_scale = 2
        self.animation_steps = {'idle': 8, 'walk_left': 8, 'walk_right': 8, 'jump':8, 'death': 6}  # amount of frames in each animation
        self.animation_speeds = {'idle': 0.15, 'walk_left': 0.15, 'jump': 0.15, 'walk_right': 0.15, 'death': 0.25}

        # Load frames immediately
        self.load_animation_frames(graphics_path)

        self.image = self.frames[self.action][0]
        self.rect = self.frames[self.action][0].get_rect(topleft = pos)
        self.player = player
        self.speed = uniform(2.5,3.5)
        self.gravity = 0.4
        self.on_ground = False
        self.is_jumping = False

        # collision
        self.obstacle_sprites = obstacle_sprites
        self.attackable_sprites = attackable_sprites
        self.hitbox = self.rect.inflate(-10 * self.enemy_scale, -5 * self.enemy_scale)
        self.dying = False
        self.horizontal_collision = False

        #enemy stats
        self.stats = {"health": 100, 'damage': 10, 'attack_cooldown': 500, 'jump_height': -12}
        self.health = self.stats['health']
        self.damage = self.stats['damage']
        self.jump_height = self.stats['jump_height']
        self.attack_cooldown = self.stats['attack_cooldown']
        self.last_attack_time = 0

        #player detection
        self.detection_radius = 350
        self.disengage_radius = 450
        self.player_detected = False



    def load_animation_frames(self, graphics_path):
        # Preload all animations so they are ready when player shoots
        sheets = {
            'idle': SpriteSheet(pygame.image.load(graphics_path / 'Orc-Walk.png').convert_alpha()),
            'walk_left': SpriteSheet(pygame.image.load(graphics_path / 'Orc-Walk.png').convert_alpha()),
            'jump': SpriteSheet(pygame.image.load(graphics_path / 'Orc-Walk.png').convert_alpha()),
            'walk_right': SpriteSheet(pygame.image.load(graphics_path / 'Orc-Walk.png').convert_alpha()),
            'death': SpriteSheet(pygame.image.load(graphics_path / 'Orc-Walk.png').convert_alpha())

        }

        for action, sheet in sheets.items():
            self.frames[action] = [sheet.get_image(i, 100, 100, self.enemy_scale) for i in range(self.animation_steps[action])]

    def apply_gravity(self):
        self.on_ground = False
        self.direction.y += self.gravity * 1.3
        self.hitbox.y += self.direction.y
        self.check_collision('vertical')
        self.rect.center = self.hitbox.center

    def move_towards_player(self):
        dx = self.player.rect.centerx - self.rect.centerx

        if abs(dx) > 5:
            self.direction.x = 1 if dx > 0 else -1
        else:
            self.direction.x = 0

        self.hitbox.x += self.direction.x * self.speed

        self.check_collision('horizontal')

        self.rect.center = self.hitbox.center

        #jump if player is above
        if self.player.rect.centery < self.rect.centery - 40 and self.horizontal_collision == True:
            self.jump()

    def jump(self):        
        if self.on_ground == True:  
            self.direction.y = self.jump_height
            self.on_ground = False
            self.is_jumping = True
            self.horizontal_collision = False

    def update_action(self):
        if self.dying:
            return

        if self.direction.length() == 0:
            self.action = 'idle'

        elif self.direction.x > 0:
            self.action = 'walk_left'

        elif self.direction.x < 0:
            self.action = 'walk_right'

        if self.is_jumping:
            self.action = 'jump'

    def check_collision(self, direction):
        if direction == 'horizontal':
            for obstacle in self.obstacle_sprites:
                if obstacle.hitbox.colliderect(self.hitbox):
                    self.horizontal_collision = True

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
                        self.on_ground = True
                        self.is_jumping = False

                    if self.direction.y < 0:
                        self.hitbox.top = obstacle.hitbox.bottom
                        self.direction.y = 0
    
    def attack_player(self):
        current_time = pygame.time.get_ticks()

        if self.hitbox.colliderect(self.player.hitbox):
            if current_time - self.last_attack_time >= self.attack_cooldown:
                self.player.take_damage(self.damage)
                self.last_attack_time = current_time

    def detect_player(self):
        distance = pygame.math.Vector2(self.player.rect.center).distance_to(self.rect.center)
        if not self.player_detected:
            if distance <= self.detection_radius:
                self.player_detected = True
        else:
            if distance >= self.disengage_radius:
                self.player_detected = False

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
            
            self.apply_gravity()
            self.update_action()

        self.animate()
