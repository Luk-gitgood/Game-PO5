import pygame
from settings import *
from spritesheets import SpriteSheet
from entity import Entity

class Player(Entity):

    def __init__(self, pos, groups, obstacle_sprites, equip_weapon, destroy_weapon):
        super().__init__(groups)
        self.obstacle_sprites = obstacle_sprites
        #Movement
        self.speed = 2
        self.gravity = 0.4
        self.jump_speed = -11
        self.jump_cut_multiplier = 0.7
        self.coyote_timer = 0.1
        self.drop_timer = 0

        #States
        self.facing_left = False
        self.is_jumping = False
        self.on_ground = False
        self.jump_held = False
        self.prev_hitbox = None

        #Graphics
        self.player_scale = 1.5
        self.sheets = {
            'idle': SpriteSheet(pygame.image.load('../graphics/animations/rogue_character/rogue_idle.png').convert_alpha()),
            'walk': SpriteSheet(pygame.image.load('../graphics/animations/rogue_character/rogue_walk.png').convert_alpha()),
            'death': SpriteSheet(pygame.image.load('../graphics/animations/rogue_character/rogue_death.png').convert_alpha()),
            'gesture': SpriteSheet(pygame.image.load('../graphics/animations/rogue_character/rogue_gesture.png').convert_alpha()),
            'jump': SpriteSheet(pygame.image.load('../graphics/animations/rogue_character/rogue_jump.png').convert_alpha()),
        }

        self.animation_steps = {'idle': 10, 'walk': 10, 'death': 10, 'gesture': 10, 'jump': 4}  #amount of frames in each animation
        self.animation_speeds = {'idle': 0.05, 'walk': 0.15, 'death': 0.1, 'gesture': 0.1, 'jump': 0.08}

        for action, sheet in self.sheets.items():
            self.frames[action] = [sheet.get_image(i, IMAGE_WIDTH, IMAGE_HEIGHT, self.player_scale) for i in range(self.animation_steps[action])]

        self.image = self.frames[self.action][0]
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(-16, 0)

        #Weapons
        self.equip_weapon = equip_weapon
        self.destroy_weapon = destroy_weapon

        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]

        #Attacking
        self.attacking = False


    def animate(self):
        super().animate()
        image = self.image
        if self.facing_left:
            image = pygame.transform.flip(image, True, False)
        self.image = image

    def update_action(self):
        #air
        if self.is_jumping:
            self.action = 'jump'
            return

        #ground
        if self.direction.x != 0:
            self.action = 'walk'
        else:
            self.action = 'idle'

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_d]:
            self.facing_left = False
            if self.direction.x < 0:
                self.direction.x = 0
            elif self.direction.x < 2:
                self.direction.x += 0.3
        elif keys[pygame.K_a]:
            self.facing_left = True
            if self.direction.x > 0:
                self.direction.x = 0
            elif self.direction.x > -2:
                self.direction.x += -0.3
        else:
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

        if keys[pygame.K_1]:
            self.equip_weapon()
            self.attacking = True

        if keys[pygame.K_g]:
            self.destroy_weapon()

    def move_horizontal(self, speed):
        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.rect.center = self.hitbox.center

    def apply_gravity(self):

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
        if self.coyote_timer > 0:
            self.direction.y = self.jump_speed
            self.coyote_timer = 0
            self.is_jumping = True

    def cut_jump(self):
        if self.direction.y < 0:
            self.direction.y *= self.jump_cut_multiplier

    def collision(self, direction):
        if direction == 'horizontal':
            for obstacle in self.obstacle_sprites:

                #Pass through platforms horizontally
                if obstacle.sprite_type == 'platform_top':
                    continue

                if obstacle.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0 : #moving right
                        self.hitbox.right = obstacle.hitbox.left
                    if self.direction.x < 0: #moving left
                        self.hitbox.left = obstacle.hitbox.right

        if direction == 'vertical':
            for obstacle in self.obstacle_sprites:
                if obstacle.hitbox.colliderect(self.hitbox):

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

    def attack_cooldowns(self):
        if self.attacking:
            pass

    def update(self):
        self.input()
        self.update_action()
        self.animate()
        self.move_horizontal(self.speed)
        self.apply_gravity()
        self.prev_hitbox = self.hitbox.copy()
        self.drop_timer = max(0, self.drop_timer - 1/60)

