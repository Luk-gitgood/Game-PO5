import pygame

class Entity(pygame.sprite.Sprite):
    
    def __init__(self, groups):
        super().__init__(groups)
        self.direction = pygame.math.Vector2()
        self.action = 'idle'
        self.frame_index = 0
        self.frames = {}
        self.flip = False

    def animate(self):
        speed = self.animation_speeds[self.action]
        self.frame_index += speed
    
        if self.frame_index >= len(self.frames[self.action]):
    
            if self.action == 'death':
                if hasattr(self, 'dead'):
                    self.dead = True
                else:
                    self.kill()
                return
    
            if hasattr(self, "is_attacking") and self.action == 'attack':
                self.is_attacking = False
                self.action = 'idle'
    
            if hasattr(self, "is_hurt") and self.action == 'hurt':
                self.is_hurt = False
                self.action = 'idle'
    
            self.frame_index = 0
    
        center = self.rect.center
        self.image = self.frames[self.action][int(self.frame_index)]

        # Check if we need to flip the image horizontally
        if self.flip:
            self.image = pygame.transform.flip(self.image, True, False)

        self.rect = self.image.get_rect(center=center)
