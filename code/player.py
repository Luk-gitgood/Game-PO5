import pygame
from settings import *
from spritesheets import SpriteSheet
from entity import Entity


class Player(Entity):
    def __init__(self, pos, groups, obstacle_sprites, equip_weapon, destroy_weapon, fire_weapon):
        super().__init__(groups)
        self.obstacle_sprites = obstacle_sprites

        #Physics
        self.gravity = 0.4
        self.jump_cut_multiplier = 0.7

        #Timers
        self.coyote_timer = 0.1
        self.drop_timer = 0

        #States
        self.facing_left = False
        self.is_jumping = False
        self.on_ground = False
        self.jump_held = False
        self.prev_hitbox = None
        self.dying = False
        self.dead = False

        #i-frames
        self.invincible = False
        self.i_frame_time = 600 #miliseconds of invincibility frames
        self.hit_time = 0

        #Stats
        self.stats = {'health': 120, 'speed': 2, 'jump_speed': -11,} #should be put in player_data.py or J'son to use upgrades
        self.health = self.stats['health']
        self.speed = self.stats['speed']
        self.jump_speed = self.stats['jump_speed']

        #dash
        self.dashing = False
        self.dash_duration = 0.2
        self.dash_timer = 0

        self.dash_cooldown = 1.5
        self.dash_last_time = -1000

        #dash tuning
        self.ground_dash_speed = 4
        self.ground_dash_duration = 0.3 #determines length of dash

        self.air_dash_speed = 5
        self.air_dash_duration = 0.01 #very small to basically disable dashing in the air. 

        #Air dash should be an unlockable / upgrade

        self.spike_damage = 10 #damage spikes do to player


        #graphics
        graphics_path = BASE_DIR.parent / 'graphics' / 'character_animations' / 'rogue_character'
        self.player_scale = 1.5
        

        self.animation_steps = {'idle': 10, 'walk': 9, 'death': 10, 'gesture': 10, 'jump': 12, 'hit': 5, 'dash': 3,}  #amount of frames in each animation
        self.animation_speeds = {'idle': 0.05, 'walk': 0.2, 'death': 0.3, 'gesture': 0.8, 'jump': 0.15, 'hit': 0.2, 'dash': 0.1} #time for each animation (in seconds)

        self.load_animation_frames(graphics_path)

        self.image = self.frames[self.action][0]
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(0, 0)

        #Weapons
        self.equip_weapon = equip_weapon
        self.destroy_weapon = destroy_weapon
        self.fire_weapon = fire_weapon

        self.weapon = 'no_weapon'
        self.can_shoot = True
        self.shoot_time = None
        self.shoot_cooldown = None

        #Attacking
        self.attacking = False

        #Keys for weapons
        self.key_2 = 'dagger'
        self.key_3 = 'revolver'
        self.key_4 = 'shotgun'
        self.key_5 = 'sniper'

    def load_animation_frames(self, graphics_path):
        #preload all animations so they are ready when player shoots
        sheets = {
            'idle': SpriteSheet(pygame.image.load(graphics_path / 'rogue_idle.png').convert_alpha()),
            'walk': SpriteSheet(pygame.image.load(graphics_path / 'rogue_walk.png').convert_alpha()),
            'death': SpriteSheet(pygame.image.load(graphics_path / 'rogue_death.png').convert_alpha()),
            'gesture': SpriteSheet(pygame.image.load(graphics_path / 'rogue_gesture.png').convert_alpha()),
            'jump': SpriteSheet(pygame.image.load(graphics_path / 'rogue_jump.png').convert_alpha()),
            'hit': SpriteSheet(pygame.image.load(graphics_path / 'rogue_hit.png').convert_alpha()),
            'dash': SpriteSheet(pygame.image.load(graphics_path / 'rogue_dash.png').convert_alpha()),
        }

        for action, sheet in sheets.items():
            self.frames[action] = [sheet.get_image(i, IMAGE_WIDTH, IMAGE_HEIGHT, self.player_scale) for i in range(self.animation_steps[action])]

    def animate(self):
        super().animate()
        if self.action == 'hit':
            if self.frame_index == 0: #hit animation only plays once
                self.action = 'idle'
        

        image = self.image
        if self.facing_left:
            image = pygame.transform.flip(image, True, False)
        self.image = image
        
    def update_action(self):
    #lock animations on death
        if self.dying:
            self.action = 'death'
            return

        if self.action == 'hit':
            return

        if self.dashing:  
            self.action = 'dash'
            return

        # air
        if self.is_jumping:
            self.action = 'jump'
            return

        # ground
        if self.direction.x != 0:
            self.action = 'walk'
        else:
            self.action = 'idle'
        
    def input(self):
        if self.dashing: #no inputs allowed when dashing
            return

        keys = pygame.key.get_pressed()

        if keys[pygame.K_d]:
            self.facing_left = False
            # Instead of resetting to 0, we accelerate
            if self.direction.x < 2: 
                self.direction.x += 0.3
        elif keys[pygame.K_a]:
            self.facing_left = True
            if self.direction.x > -2:
                self.direction.x -= 0.3
        else:
            self.direction.x *= 0.8 #don't stop moving abrubtly
            if abs(self.direction.x) < 0.1:
                self.direction.x = 0

        if keys[pygame.K_SPACE]:
            if not self.jump_held:
                self.jump()
            self.jump_held = True
        else:
            if self.jump_held:
                self.cut_jump()
            self.jump_held = False

        if keys[pygame.K_s] and self.on_ground:
            self.drop_timer = 0.2
            self.direction.y = 1

        if keys[pygame.K_LSHIFT]: #dash keybind. (probably shouldn't do it with pygame.key.get_pressed, because it causes inconsistent dashes)
            self.start_dash()
            
        """different weapon keybinds. For now all are available at every point in the game. TODO should be locked behind certain objectives or upgrades"""
        if keys[pygame.K_1]:
            self.destroy_weapon()
            self.weapon_equipped = False
            self.weapon = 'no_weapon'

        if keys[pygame.K_2]:
            if self.weapon != self.key_2:
                self.switch_weapon(self.key_2)

        if keys[pygame.K_3]:
            if self.weapon != self.key_3:
                self.switch_weapon(self.key_3)

        if keys[pygame.K_4]: 
            if self.weapon != self.key_4:
                self.switch_weapon(self.key_4)

        if keys[pygame.K_5]:
            if self.weapon != self.key_5:
                self.switch_weapon(self.key_5)


        #mouse detection for shooting. Only shoots if weapon is equipped and cooldown is ready.
        if pygame.mouse.get_pressed()[0]:  # Left Click
            if self.weapon != 'no_weapon' and self.can_shoot:
                self.fire_weapon()
                self.can_shoot = False
                self.shoot_time = pygame.time.get_ticks()

    def switch_weapon(self, weapon):
        self.destroy_weapon()
        self.weapon = weapon
        self.shoot_cooldown = all_weapon_data[self.weapon]['cooldown']
        self.equip_weapon(self.weapon)

    def move_horizontal(self, speed):
        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.rect.center = self.hitbox.center

    def apply_gravity(self):
        #doesnt completely ignore gravity when dashing but weakens gravity
        if self.dashing: 
            self.direction.y += self.gravity * 0.3
            self.hitbox.y += self.direction.y
            self.collision('vertical') #prevents falling out of the map when dashing while self.on_ground
            self.rect.center = self.hitbox.center
            return

        if self.on_ground:
            self.coyote_timer = 0.1
        else:
            self.coyote_timer -= 1/60

        self.on_ground = False
        self.direction.y += self.gravity * 1.3
        self.hitbox.y += self.direction.y
        self.collision('vertical')
        self.rect.center = self.hitbox.center

    def jump(self):
        if self.dashing:
            return

        if self.coyote_timer > 0:
            self.direction.y = self.jump_speed
            self.coyote_timer = 0
            self.is_jumping = True

    def cut_jump(self):
        if self.direction.y < 0:
            self.direction.y *= self.jump_cut_multiplier

    def start_dash(self):
        current_time = pygame.time.get_ticks() / 1000

        if self.dashing:
            return

        if current_time - self.dash_last_time < self.dash_cooldown:
            return

        #check ground based on immediate hitbox collision (self.on_ground is wonky)
        on_ground_now = False
        for obstacle in self.obstacle_sprites:
            if obstacle.sprite_type != 'platform_top':
                continue
            if self.hitbox.bottom == obstacle.hitbox.top:
                on_ground_now = True
                break

        self.dashing = True
        self.action = 'dash'
        self.frame_index = 0  #reset animation frame to start from beginning
        self.dash_last_time = current_time #enables dash cooldown check

        #choose dash type
        if on_ground_now:
            dash_speed = self.ground_dash_speed
            self.dash_timer = self.ground_dash_duration
        else:
            dash_speed = self.air_dash_speed
            self.dash_timer = self.air_dash_duration

        # i-frames
        self.invincible = True 
        self.hit_time = pygame.time.get_ticks()

        # direction
        if self.facing_left:
            self.direction.x = -dash_speed
        else:
            self.direction.x = dash_speed

    def dash_update(self, dt):

        if not self.dashing:
            return

        self.dash_timer -= dt

        #slow down gradually at the end of dash
        if self.dash_timer <0.1:
            self.direction.x *= 0.85

        if self.dash_timer <= 0:
            self.dashing = False
            self.direction.x *= 0.6 #carry speed from dash (smoother)



    def collision(self, direction):
        if direction == 'horizontal':
            for obstacle in self.obstacle_sprites:

                #Pass through platforms horizontally
                if obstacle.sprite_type == 'platform_top':
                    continue

                if obstacle.hitbox.colliderect(self.hitbox):
                    if obstacle.sprite_type == 'damage':
                        self.take_damage(self.spike_damage)
                        
                    if self.direction.x > 0 : #moving right
                        self.hitbox.right = obstacle.hitbox.left
                    if self.direction.x < 0: #moving left
                        self.hitbox.left = obstacle.hitbox.right

        if direction == 'vertical':
            for obstacle in self.obstacle_sprites:
                if obstacle.hitbox.colliderect(self.hitbox):
                    if obstacle.sprite_type == 'damage':
                        self.take_damage(10) 

                    if self.direction.y > 0:

                        if obstacle.sprite_type == 'platform_top':

                            if self.drop_timer > 0:
                                continue

                            elif self.prev_hitbox.bottom <= obstacle.hitbox.top:
                                self.hitbox.bottom = obstacle.hitbox.top
                                self.direction.y = 0
                                self.on_ground = True
                                self.is_jumping = False
                        else:
                            self.hitbox.bottom = obstacle.hitbox.top
                            self.direction.y = 0
                            self.on_ground = True
                            self.is_jumping = False

                    if self.direction.y < 0:
                        if obstacle.sprite_type != 'platform_top':
                            self.hitbox.top = obstacle.hitbox.bottom
                            self.direction.y = 0

                   
    
    def take_damage(self, amount):
        if self.dying or self.invincible:
            return

        self.health -= amount
            
        self.invincible = True
        self.hit_time = pygame.time.get_ticks()
        self.action = 'hit'
        self.frame_index = 0

        if self.health <= 0:
            self.health = 0
            self.dying = True
            self.action = 'death'
            self.frame_index = 0
            self.speed = 0



    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if not self.can_shoot:
            if current_time - self.shoot_time >= self.shoot_cooldown:
                self.can_shoot = True

        if self.invincible:     #i-frame cooldown checker
            if current_time - self.hit_time >= self.i_frame_time:
                self.invincible = False

    def update(self):
        if self.dead:
            return

        dt = 1/60

        self.prev_hitbox = self.hitbox.copy()
        self.input()
        self.cooldowns()
        self.dash_update(dt)
        self.update_action()
        self.animate()
        self.move_horizontal(self.speed)
        self.apply_gravity()
        
        self.drop_timer = max(0, self.drop_timer - dt)

