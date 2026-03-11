import pygame
from spritesheets import SpriteSheet
from entity import Entity
from settings import *
from random import uniform
from enemy_data import ENEMY_DATA


class WalkingEnemy(Entity):

    def __init__(self, pos, groups, player, obstacle_sprites, attackable_sprites, enemy_type):
        super().__init__(groups)
        self.data = ENEMY_DATA[enemy_type]
        self.stats = self.data['stats']
        self.player = player

        graphics_path = BASE_DIR.parent / 'graphics' / 'character_animations' / self.data['path']
        self.enemy_scale = self.data['scale']
        self.animation_steps = self.data['animation_steps']
        self.animation_speeds = self.data['animation_speeds']

        self.load_animation_frames(graphics_path)

        self.image = self.frames[self.action][0]
        self.rect = self.frames[self.action][0].get_rect(topleft = pos)

        #physics
        self.gravity = 0.4

        #collision
        self.obstacle_sprites = obstacle_sprites
        self.attackable_sprites = attackable_sprites
        self.hitbox = self.rect.inflate(0,0)
        self.dying = False
        self.horizontal_collision = False
        self.damage_applied = False

        #state flags
        self.is_attacking = False
        self.is_hurt = False
        self.is_jumping = False
        self.on_ground = False

        #enemy stats
        self.health = self.stats['health']
        self.damage = self.stats['damage']
        self.jump_height = self.stats['jump_height']
        self.attack_cooldown = self.stats['attack_cooldown']
        self.last_attack_time = 0
        self.speed = uniform(*self.stats['speed'])

        # player detection
        self.detection_radius = self.stats['detection_radius']
        self.disengage_radius = self.stats['disengage_radius']
        self.player_detected = False

        #Movement Variables
        self.accel = 0.4      
        self.friction = 0.2    
        self.max_speed = self.speed 
        self.direction.x = 0   
        self.look_ahead_dist = 30 


    def load_animation_frames(self, graphics_path):
        sheets = {}
        for key,value in self.data['sheets'].items():
            sheets[key] = SpriteSheet(pygame.image.load(graphics_path / value).convert_alpha())

        for action, sheet in sheets.items():
            self.frames[action] = [sheet.get_image(i, self.data['size']['width'], self.data['size']['height'], self.enemy_scale) for i in range(self.animation_steps[action])]


    def apply_gravity(self):
        self.on_ground = False
        self.direction.y += self.gravity * 1.3
        self.hitbox.y += self.direction.y
        self.check_collision('vertical')
        self.rect.center = self.hitbox.center


    def move_towards_player(self):
            if self.is_attacking:
                self.direction.x = 0
                return
    
            dx = self.player.rect.centerx - self.rect.centerx
            
            #ACCELERATION LOGIC
            if abs(dx) > 10:
                target_vel = 1 if dx > 0 else -1
    
                #Gradually nudge current velocity toward target
                self.direction.x += target_vel * self.accel
    
            else:
                #FRICTION LOGIC (Slow down when close)
                if self.direction.x > 0:
                    self.direction.x = max(0, self.direction.x - self.friction)
                elif self.direction.x < 0:
                    self.direction.x = min(0, self.direction.x + self.friction)
    
            # Limit to max speed
            if abs(self.direction.x) > 1: 
                self.direction.x = 1 if self.direction.x > 0 else -1
    
            self.jump()
    
            #Apply horizontal movement
            self.hitbox.x += self.direction.x * self.max_speed
            self.check_collision('horizontal')
            self.rect.center = self.hitbox.center


    def jump(self):
        if not self.on_ground: return

        #sensor rect in front of the enemy
        look_dist = self.look_ahead_dist if self.direction.x >= 0 else -self.look_ahead_dist
        sensor_rect = self.hitbox.copy()
        sensor_rect.x += look_dist

        for obstacle in self.obstacle_sprites:
            if obstacle.hitbox.colliderect(sensor_rect):
                #If player is higher than enemy and there is a wall ahead jump
                if self.player.rect.centery < self.rect.centery - 20:
                    self.direction.y = self.jump_height
                    self.on_ground = False
                    self.is_jumping = True
                    self.horizontal_collision = False
                    break


    def update_action(self):
            if self.dying or self.is_attacking or self.is_hurt:
                return 
    
            # Using a small threshold because friction makes velocity float
            if abs(self.direction.x) < 0.1:
                self.action = 'idle'
                self.direction.x = 0 
            else:
                self.action = 'walk'
    
            if self.direction.x > 0: self.flip = False
            elif self.direction.x < 0: self.flip = True


    def check_collision(self, direction):

        if direction == 'horizontal':
            self.horizontal_collision = False

            for obstacle in self.obstacle_sprites:
                if obstacle.hitbox.colliderect(self.hitbox):

                    self.horizontal_collision = True

                    if self.direction.x > 0:
                        self.hitbox.right = obstacle.hitbox.left
                    if self.direction.x < 0:
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
    
        if self.is_hurt or self.dying:
            return
    
        current_time = pygame.time.get_ticks()
    
        # start attack
        if not self.is_attacking:
    
            if self.hitbox.colliderect(self.player.hitbox):
    
                if current_time - self.last_attack_time >= self.attack_cooldown:
                    self.is_attacking = True
                    self.action = 'attack'
                    self.frame_index = 0
                    self.damage_applied = False
                    self.last_attack_time = current_time
    
        # deal damage during attack animation
        if self.is_attacking and not self.damage_applied:
    
            if int(self.frame_index) == self.animation_steps['attack'] - 2:   # attack hit frame
    
                if self.hitbox.colliderect(self.player.hitbox):
                    self.player.take_damage(self.damage)
    
                self.damage_applied = True


    def detect_player(self):

        distance = pygame.math.Vector2(self.player.rect.center).distance_to(self.rect.center)

        if not self.player_detected:
            if distance <= self.detection_radius:
                self.player_detected = True
        else:
            if distance >= self.disengage_radius:
                self.player_detected = False

    def can_see_player(self):
        #Get the start and end points of the "ray"
        start = self.rect.center
        end = self.player.rect.center
    
        #Check every obstacle to see if it "clips" (intersects) this line
        for obstacle in self.obstacle_sprites:
            #Skips platform_tops (so it can see through platforms tops)
            if obstacle.sprite_type == 'platform_top':
                continue
            else:
                # clipline returns a tuple of points if it hits, or an empty tuple if it doesn't
                if obstacle.hitbox.clipline(start, end):
                    return False # View is blocked!
                
        return True


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
            return

        if not self.is_attacking:
            self.is_hurt = True
            self.action = 'hurt'
            self.frame_index = 0


    def draw_health_bar(self,surface,offset):

        if self.health >= self.stats['health']:
            return

        bar_x = self.rect.centerx - ENEMY_BAR_WIDTH // 2 - offset.x
        bar_y = self.rect.top - BAR_OFFSET_Y - offset.y

        bg_rect = pygame.Rect(bar_x, bar_y, ENEMY_BAR_WIDTH, ENEMY_BAR_HEIGHT)
        pygame.draw.rect(surface, UI_BG_COLOR, bg_rect)

        ratio = self.health / self.stats['health']
        current_width = bg_rect.width * ratio
        current_rect = bg_rect.copy()
        current_rect.width = current_width

        pygame.draw.rect(surface, HEALTH_COLOR, current_rect)


    def update(self):
        if not self.dying:
            self.detect_player()
    
            # Only check Line of Sight if they are within range
            if self.player_detected and self.can_see_player():
                if not self.is_attacking:
                    self.move_towards_player()
                self.attack_player()
            else:
                self.direction.x = 0
    
            self.apply_gravity()
            self.update_action()
    
        self.animate()