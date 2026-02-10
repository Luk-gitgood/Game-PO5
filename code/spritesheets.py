import pygame

class SpriteSheet:
    def __init__(self, image):
        self.sheet = image

    def get_image(self, frame, width, height, scale):
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), ((frame * width), 0, width, height))
        image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        return image.convert_alpha()

#this funcion gets a list of images from a spritesheet and given the row, frames, width height and a scale factor, it returns a list of images that can be used for animation in player.py.
#this function scales the image, which makes the original 32x32 sprite bigger. Scaling like this is not good and we should use 32x64 sprites instead, but for now it works and looks fine.