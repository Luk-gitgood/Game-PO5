import pygame

class Entity(pygame.sprite.Sprite):
    
    def __init__(self, groups):
        super().__init__(groups)
        self.direction = pygame.math.Vector2()
        self.action = 'idle'
        self.frame_index = 0
        self.frames = {}

    def animate(self):
        speed = self.animation_speeds[self.action]
        self.frame_index += speed
        if self.frame_index >= len(self.frames[self.action]):
            if self.action == 'death':
                self.kill()
                return
            self.frame_index = 0
        self.image = self.frames[self.action][int(self.frame_index)]

