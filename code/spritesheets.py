import pygame

class SpriteSheet:
    def __init__(self, image):
        self.sheet = image

    def get_image(self, frame, width, height, scale):
        #Extract the raw frame
        raw_frame = pygame.Surface((width, height), pygame.SRCALPHA)
        raw_frame.blit(self.sheet, (0, 0), ((frame * width), 0, width, height))
        
        #Find the actual content (removes the empty padding)
        trim_rect = raw_frame.get_bounding_rect()
        trimmed_surface = pygame.Surface(trim_rect.size, pygame.SRCALPHA)
        trimmed_surface.blit(raw_frame, (0, 0), trim_rect)
        
        #Scale the trimmed version
        scaled_width = int(trim_rect.width * scale)
        scaled_height = int(trim_rect.height * scale)
        final_image = pygame.transform.scale(trimmed_surface, (scaled_width, scaled_height))
        
        return final_image.convert_alpha()
#this funcion gets a list of images from a spritesheet and given the row, frames, width height and a scale factor, it returns a list of images that can be used for animation in player.py.
#this function scales the image, which makes the original 32x32 sprite bigger. Scaling like this is not good and we should use 32x64 sprites instead, but for now it works and looks fine.