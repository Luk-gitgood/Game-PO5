import pygame
import math
from audio import AudioManager
from spritesheets import SpriteSheet
from settings import *
from bullet import Bullet
from random import uniform

class Weapon(pygame.sprite.Sprite):
    def __init__(self, groups, player, obstacle_sprites, attackable_sprites, offset, weapon_type):
        super().__init__(groups)

        graphics_path = BASE_DIR.parent / 'graphics' / 'weapons'
        self.groups = groups
        self.player = player
        self.obstacle_sprites = obstacle_sprites
        self.attackable_sprites = attackable_sprites
        self.offset = offset
        self.weapon_type = weapon_type

        self.weapon_data = all_weapon_data[self.weapon_type]
        self.dagger_attack_timer = 100 #used for the attack movement of the dagger

        #SFX
        self.sfx = AudioManager(
            {
            'revolver': SFX_PATH / 'revolver_shot.ogg',
            'shotgun': SFX_PATH / 'shotgun_shot2.ogg',
            'sniper': SFX_PATH / 'sniper_shot.ogg',
            })

        #Static Setup
        full_path = f"{graphics_path}/{self.weapon_type}.png"
        self.original_image = pygame.image.load(full_path).convert_alpha()
        self.flipped_image = pygame.transform.flip(self.original_image, False, True)

        self.image = self.original_image
        self.angle = 0

        #offset = 40

        #User screen size
        info = pygame.display.Info()
        MONITOR_WIDTH = info.current_w
        MONITOR_HEIGHT = info.current_h


        #Changed weapon spawn so that it spawns with correct direction (moved parts of update to init)
        #Position and direction logic
        scale_x = BASE_SCREEN_WIDTH / MONITOR_WIDTH
        scale_y = BASE_SCREEN_HEIGHT / MONITOR_HEIGHT
        mouse_pos = pygame.mouse.get_pos()

        #convert mouse from real screen resolution to base resolution
        mouse_scaled = pygame.math.Vector2(mouse_pos[0] * scale_x,mouse_pos[1] * scale_y)
        mouse_world = mouse_scaled + self.player.groups()[0].offset

        self.direction = pygame.math.Vector2(mouse_world) - pygame.math.Vector2(self.player.rect.center)
        self.weapon_pos = pygame.math.Vector2(self.player.rect.center) + self.direction * 40

        self.rect = self.image.get_rect(center=self.weapon_pos)

        #Animation Setup
        self.action = 'idle'
        self.frame_index = 0
        self.frames = []

        self.weapon_size = self.weapon_data['size']
        self.animation_steps = self.weapon_data['animation_steps']
        self.animation_speeds = self.weapon_data['animation_speeds']

        #Load frames immediately
        if self.animation_speeds != 1:
            self.load_animation_frames(graphics_path)


    def load_animation_frames(self, path):
        # Preload all animations so they are ready when player shoots
        sheet = SpriteSheet(pygame.image.load(path / f'{self.weapon_type}_animation.png').convert_alpha())
        self.frames = [sheet.get_image(i, self.weapon_size[0], self.weapon_size[1], 1)for i in range(self.animation_steps)]


    def shoot(self):
        #Only start animation if player isn't already shooting
        if self.action == 'idle':
            self.action = self.weapon_type
            self.frame_index = 0


            #Shooting
            for _ in range(self.weapon_data['bullet_count']):
                spread = uniform(-self.weapon_data['spread'], self.weapon_data['spread'])
                Bullet(self.rect.center, self.angle + spread, self.groups, self.obstacle_sprites, self.attackable_sprites, self.weapon_data['speed'],
                       self.weapon_data['lifetime'], self.weapon_data['damage'])

            if self.weapon_type == 'dagger':
                self.dagger_attack_timer = 0

            #Knockback
            if self.weapon_type == 'shotgun':
                if self.direction.length() != 0:
                    self.player.direction += self.direction.normalize() * -1 #determines amount of recoil / knockback

            #Sound
                self.sfx.play_sfx('shotgun', volume=0.5)

            elif self.weapon_type == 'revolver':
                self.sfx.play_sfx('revolver')

            elif self.weapon_type =='sniper':
                self.sfx.play_sfx('sniper')

    def stab(self):
        #offset moving for dagger animation
        if self.dagger_attack_timer == 100:
            self.offset = 30
        elif self.dagger_attack_timer == 50:
            self.offset = 40
        elif self.dagger_attack_timer == 0:
            self.offset = 50
            # dagger damage hitboxes
            for sprite in self.attackable_sprites:
                if sprite.hitbox.colliderect(self.rect):
                    sprite.take_damage(self.weapon_data['damage'])

        if self.dagger_attack_timer !=100:
            self.dagger_attack_timer += 5



    def animate(self):
        #Only use if in a shooting state
        if self.action != 'idle':
            self.frame_index += self.animation_speeds
            

            if self.frame_index >= len(self.frames): #back to starting frame (index 0) after animation finishes
                self.frame_index = 0
                self.action = 'idle'  # Back to static image

    def update(self):
        #User screen size
        info = pygame.display.Info()
        MONITOR_WIDTH = info.current_w
        MONITOR_HEIGHT = info.current_h

        #Position and direction logic
        scale_x = BASE_SCREEN_WIDTH / MONITOR_WIDTH
        scale_y = BASE_SCREEN_HEIGHT / MONITOR_HEIGHT

        mouse_pos = pygame.mouse.get_pos()

        #convert mouse from real screen resolution to base resolution
        mouse_scaled = pygame.math.Vector2(
            mouse_pos[0] * scale_x,
            mouse_pos[1] * scale_y
        )

        mouse_world = mouse_scaled + self.player.groups()[0].offset


        self.direction = pygame.math.Vector2(mouse_world) - pygame.math.Vector2(self.player.rect.center)


        if self.direction.length() != 0:
            self.direction = self.direction.normalize()

        self.angle = math.degrees(math.atan2(self.direction.y, self.direction.x))
        self.weapon_pos = pygame.math.Vector2(self.player.rect.center) + self.direction * self.offset

        #run animation logic
        self.animate()

        #Select the base image BEFORE rotating
        if self.action == 'idle':
            # Use static PNGs
            base_img = self.original_image
            flipped_base = self.flipped_image
        else:
            # Use current animation frame
            base_img = self.frames[int(self.frame_index)]
            flipped_base = pygame.transform.flip(base_img, False, True)

        #Rotate the correct base image (animation frame / static)
        if 90 > self.angle > -90:
            self.image = pygame.transform.rotate(base_img, -self.angle)
        else:
            self.image = pygame.transform.rotate(flipped_base, -self.angle)

        self.rect = self.image.get_rect(center=self.weapon_pos)

        if self.weapon_type == 'dagger':
            self.stab()