import pygame
from settings import *
from spritesheets import SpriteSheet
from entity import Entity

class Player(Entity):
    """
    De hoofdrolspeler van het spel, beheerd door de gebruiker.

    Deze klasse breidt de basis Entity uit met specifieke platformer-mechanieken zoals
    jump physics (inclusief variable jump height), coyote time, horizontal movement
    met versnelling/vertraging, en een dash-systeem. Ook beheert het de combat-logica,
    wapenwissels en animatie-states.

    Attributes:
        health (int): De huidige levenspunten van de speler.
        speed (float): De horizontale bewegingssnelheid.
        invincible (bool): Vlag die aangeeft of de speler tijdelijk onkwetsbaar is (i-frames).
        dashing (bool): Vlag die aangeeft of de speler momenteel een dash uitvoert.
        on_ground (bool): Geeft aan of de speler contact maakt met een vloer/platform.
        weapon (str): De naam van het momenteel uitgeruste wapen.
        hitbox (pygame.Rect): De actuele collision box van de speler.
    """

    def __init__(self, pos, groups, obstacle_sprites, equip_weapon, destroy_weapon, fire_weapon):
        """
        Initialiseert de speler met physics-parameters, timers, stats en animaties.

        Args:
            pos (tuple): Startpositie (x, y).
            groups (list): Sprite-groepen waaraan de speler toegevoegd moet worden.
            obstacle_sprites (pygame.sprite.Group): Groep met tiles voor collision-detectie.
            equip_weapon (function): Callback om een wapen te spawnen.
            destroy_weapon (function): Callback om een wapen te verwijderen.
            fire_weapon (function): Callback om het wapen te laten vuren.
        """
        super().__init__(groups)
        self.obstacle_sprites = obstacle_sprites

        # Physics instellingen
        self.gravity = 0.4
        self.jump_cut_multiplier = 0.7  # Voor kortere sprongen bij kort indrukken

        # Timers voor 'game feel'
        self.coyote_timer = 0.1         # Speling om nog te springen net na een afgrond
        self.drop_timer = 0             # Timer om door one-way platforms te zakken

        # Toestanden (States)
        self.facing_left = False
        self.is_jumping = False
        self.on_ground = True
        self.jump_held = False
        self.prev_hitbox = None         # Gebruikt voor betrouwbare platform-collision
        self.dying = False
        self.dead = False

        # Onkwetsbaarheid (i-frames)
        self.invincible = False
        self.i_frame_time = 400         # Duur in milliseconden
        self.hit_time = 0

        # Basis stats
        self.stats = {'health': 120, 'speed': 2, 'jump_speed': -11}
        self.health = self.stats['health']
        self.speed = self.stats['speed']
        self.jump_speed = self.stats['jump_speed']

        # Dash mechanisme
        self.dashing = False
        self.dash_duration = 0.2
        self.dash_timer = 0
        self.dash_cooldown = 1.5
        self.dash_last_time = -1000
        self.ground_dash_speed = 4
        self.ground_dash_duration = 0.3
        
        
        self.spike_damage = 10

        # dash tuning
        self.ground_dash_speed = 5
        self.ground_dash_duration = 0.3 #determines length of dash

        self.air_dash_speed = 5
        self.air_dash_duration = 0.3 

        # Grafische configuratie
        graphics_path = BASE_DIR.parent / 'graphics' / 'character_animations' / 'rogue_character'
        self.player_scale = 1.5
        self.animation_steps = {'idle': 10, 'walk': 9, 'death': 10, 'gesture': 10, 'jump': 12, 'hit': 5, 'dash': 3}
        self.animation_speeds = {'idle': 0.05, 'walk': 0.2, 'death': 0.3, 'gesture': 0.8, 'jump': 0.15, 'hit': 0.2, 'dash': 0.1}

        self.load_animation_frames(graphics_path)

        # Hitbox setup (Inflate kan gebruikt worden om de collision box te verkleinen/vergroten)
        self.image = self.frames[self.action][0]
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(0, 0)

        # Wapen callbacks en keybinds
        self.equip_weapon = equip_weapon
        self.destroy_weapon = destroy_weapon
        self.fire_weapon = fire_weapon
        self.weapon = 'no_weapon'
        self.can_shoot = True
        self.shoot_time = None
        self.shoot_cooldown = None

        self.key_2 = 'dagger'
        self.key_3 = 'revolver'
        self.key_4 = 'shotgun'
        self.key_5 = 'sniper'
        #Attacking
        self.attacking = False


    def load_animation_frames(self, graphics_path):
        """Laadt alle spritesheets in en knipt ze op in individuele frames per actie."""
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
        """Verwerkt de huidige animatie-frame en spiegelt de sprite indien nodig."""
        super().animate()
        if self.action == 'hit':
            if self.frame_index == 0: 
                self.action = 'idle'

        image = self.image
        if self.facing_left:
            image = pygame.transform.flip(image, True, False)
        self.image = image
        
    def update_action(self):
        """Bepaalt welke animatie-state actief moet zijn op basis van beweging en status."""
        if self.dying:
            self.action = 'death'
            return
        if self.action == 'hit':
            return
        if self.dashing:  
            self.action = 'dash'
            return
        if self.is_jumping:
            self.action = 'jump'
            return
        if self.direction.x != 0:
            self.action = 'walk'
        else:
            self.action = 'idle'
        
    def input(self):
        """Registreert toetsenbord- en muisinput voor beweging, wapenwissels en vuren."""
        if self.dashing: 
            return

        keys = pygame.key.get_pressed()

        # Horizontale beweging met versnelling
        if keys[pygame.K_d]:
            self.facing_left = False
            if self.direction.x < 0: self.direction.x = 0
            elif self.direction.x < 2: self.direction.x += 0.3
        elif keys[pygame.K_a]:
            self.facing_left = True
            if self.direction.x > 0: self.direction.x = 0
            elif self.direction.x > -2: self.direction.x += -0.3

        else:
            self.direction.x *= 0.8 # Uitvloeien van beweging
            if abs(self.direction.x) < 0.1: self.direction.x = 0

        # Springen en Variable Jump Height
        if keys[pygame.K_SPACE]:
            if not self.jump_held: self.jump()
            self.jump_held = True
        else:
            if self.jump_held: self.cut_jump()
            self.jump_held = False

        # Bukken / Door platform zakken
        if keys[pygame.K_s] and self.on_ground:
            self.drop_timer = 0.2
            self.direction.y = 1

        if keys[pygame.K_LSHIFT]:
            self.start_dash()
            
        # Wapen selectie
        if keys[pygame.K_1]:
            self.destroy_weapon()
            self.weapon = 'no_weapon'
        elif keys[pygame.K_2]:
            if self.weapon != self.key_2: self.switch_weapon(self.key_2)
        elif keys[pygame.K_3]:
            if self.weapon != self.key_3: self.switch_weapon(self.key_3)
        elif keys[pygame.K_4]: 
            if self.weapon != self.key_4: self.switch_weapon(self.key_4)
        elif keys[pygame.K_5]:
            if self.weapon != self.key_5: self.switch_weapon(self.key_5)

        # Vuren
        if pygame.mouse.get_pressed()[0]:
            if self.weapon != 'no_weapon' and self.can_shoot:
                self.fire_weapon()
                self.can_shoot = False
                self.shoot_time = pygame.time.get_ticks()

    def switch_weapon(self, weapon):
        """Wisselt het huidige wapen en reset de cooldown."""
        self.destroy_weapon()
        self.weapon = weapon
        self.shoot_cooldown = all_weapon_data[self.weapon]['cooldown']
        self.equip_weapon(self.weapon)

    def move_horizontal(self, speed):
        """Verplaatst de speler horizontaal en controleert op collisions."""
        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.rect.center = self.hitbox.center

    def apply_gravity(self):
        """Past zwaartekracht toe en handelt coyote-time en verticale collisions af."""
        if self.dashing: 
            self.direction.y += self.gravity * 0.3
            self.hitbox.y += self.direction.y
            self.collision('vertical')
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
        """Laat de speler springen indien op de grond of binnen coyote-time."""
        if not self.dashing and self.coyote_timer > 0:
            self.direction.y = self.jump_speed
            self.coyote_timer = 0
            self.is_jumping = True

    def cut_jump(self):
        """Vermindert de opwaartse snelheid als de sprongknop vroegtijdig wordt losgelaten."""
        if self.direction.y < 0:
            self.direction.y *= self.jump_cut_multiplier

    def start_dash(self):
        """Initialiseert de dash-beweging, inclusief cooldown en i-frames."""
        current_time = pygame.time.get_ticks() / 1000
        if self.dashing or (current_time - self.dash_last_time < self.dash_cooldown): #als de huidige tijd - laatste keer dashen kleiner is dan dash cooldown, dashing niet toegestaan
            return

        # Directe check voor grond-collision
        on_ground_now = any(o.sprite_type == 'platform_top' and self.hitbox.bottom == o.hitbox.top for o in self.obstacle_sprites)

        self.dashing = True
        self.action = 'dash'
        self.frame_index = 0
        self.dash_last_time = current_time

        if on_ground_now:
            dash_speed = self.ground_dash_speed
            self.dash_timer = self.ground_dash_duration
        else:
            dash_speed = self.air_dash_speed
            self.dash_timer = self.air_dash_duration

        self.invincible = True 
        self.hit_time = pygame.time.get_ticks()
        self.direction.x = -dash_speed if self.facing_left else dash_speed

    def dash_update(self, dt):
        """Update de dash-timer en vertraagt de speler aan het einde van de dash (smoother)."""
        if not self.dashing: return
        self.dash_timer -= dt
        if self.dash_timer < 0.1:
            self.direction.x *= 0.85
        if self.dash_timer <= 0:
            self.dashing = False
            self.direction.x *= 0.6 

    def collision(self, direction):
        """
        Handelt botsingen af met muren en platforms.
        
        Speciale logica voor 'platform_top' zorgt ervoor dat de speler alleen van bovenaf
        landt en doorheen kan zakken bij een 'drop' command.
        """
        if direction == 'horizontal':
            for obstacle in self.obstacle_sprites:
                #pass through platforms horizontally
                if obstacle.sprite_type == 'platform_top':
                    continue

                if obstacle.hitbox.colliderect(self.hitbox):
                    if obstacle.sprite_type == 'damage':
                        self.take_damage(self.spike_damage)
                        continue  #damage tiles hurt but don't block movement

                    if self.direction.x > 0:  # moving right
                        self.hitbox.right = obstacle.hitbox.left
                    if self.direction.x < 0:  # moving left
                        self.hitbox.left = obstacle.hitbox.right

        if direction == 'vertical':
            for obstacle in self.obstacle_sprites:
                if obstacle.hitbox.colliderect(self.hitbox):
                    if obstacle.sprite_type == 'damage':
                        self.take_damage(self.spike_damage)
                        continue  #damage tiles doen damage, maar blokkeren niet de movement

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

                    elif self.direction.y < 0: # Omhoog bewegen
                        if obstacle.sprite_type != 'platform_top':
                            self.hitbox.top = obstacle.hitbox.bottom
                            self.direction.y = 0
        
    def take_damage(self, amount):
        """Vermindert health en start i-frames of dood-animatie."""
        if self.dying or self.invincible: return
        self.health -= amount
        self.invincible = True
        self.hit_time = pygame.time.get_ticks()
        self.action = 'hit'
        self.frame_index = 0

        if self.health <= 0:
            self.health = 0
            self.dying = True
            self.speed = 0

    def cooldowns(self):
        """Beheert timers voor schieten en onkwetsbaarheid."""
        current_time = pygame.time.get_ticks()
        if not self.can_shoot:
            if current_time - self.shoot_time >= self.shoot_cooldown:
                self.can_shoot = True

        if self.invincible:
            if current_time - self.hit_time >= self.i_frame_time:
                self.invincible = False

    def update(self):
        """De frame-by-frame update van de speler."""
        if self.dead: return
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





