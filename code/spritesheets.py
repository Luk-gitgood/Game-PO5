import pygame

class SpriteSheet:
    """
    Een hulpmiddel voor het beheren en uitsnijden van spritesheets.

    Deze klasse snijdt individuele frames uit een grotere afbeelding (sheet). 
    Het bevat logica om automatisch transparante randen te verwijderen (trimmen) 
    voordat de sprite wordt geschaald, wat zorgt voor consistentere sprites 
    en betere collision-detectie.

    Attributes:
        sheet (pygame.Surface): De bronafbeelding die alle animatieframes bevat.
    """

    def __init__(self, image):
        """
        Initialiseert de SpriteSheet met een geladen afbeelding.

        Args:
            image (pygame.Surface): De afbeelding die als sheet dient.
        """
        self.sheet = image

    def get_image(self, frame, width, height, scale):
        """
        Extraheert een specifiek frame, trimt de loze ruimte en schaalt het resultaat.

        De methode gebruikt 'get_bounding_rect()' om de daadwerkelijke pixels te vinden, 
        waardoor lege ruimte rondom de sprite in de spritesheet geen invloed heeft 
        op de uiteindelijke sprite-grootte in de game.

        Args:
            frame (int): De index van het frame (0, 1, 2, ...).
            width (int): De breedte van een enkel frame in de bronafbeelding.
            height (int): De hoogte van een enkel frame in de bronafbeelding.
            scale (float): De factor waarmee de getrimde sprite vergroot moet worden.

        Returns:
            pygame.Surface: De bewerkte sprite, klaar voor gebruik in een animatielijst.
        """
        #Extraheer het ruwe frame uit de sheet
        raw_frame = pygame.Surface((width, height), pygame.SRCALPHA)
        raw_frame.blit(self.sheet, (0, 0), ((frame * width), 0, width, height))
        
        #Vind de werkelijke inhoud (verwijdert de lege padding)
        # get_bounding_rect vindt de kleinste rechthoek die alle niet-transparante pixels bevat.
        trim_rect = raw_frame.get_bounding_rect()
        trimmed_surface = pygame.Surface(trim_rect.size, pygame.SRCALPHA)
        trimmed_surface.blit(raw_frame, (0, 0), trim_rect)
        
        #Schaal de getrimde versie
        scaled_width = int(trim_rect.width * scale)
        scaled_height = int(trim_rect.height * scale)
        final_image = pygame.transform.scale(trimmed_surface, (scaled_width, scaled_height))
        
        return final_image.convert_alpha()