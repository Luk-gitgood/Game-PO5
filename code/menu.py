import pygame
from settings import *

class Button:
    """
    Een interactieve knop die van uiterlijk verandert bij hooveren en klik-events detecteert.

    De knop maakt gebruik van ankerpunten (bijv. 'center', 'topleft') om relatief 
    ten opzichte van de surface geplaatst te worden, wat handig is bij verschillende resoluties.

    Attributes:
        surface (pygame.Surface): De surface waarop de knop getekend wordt.
        rect (pygame.Rect): De hitbox en positie van de knop.
        anchor (str): Het ankerpunt op de surface (bijv. 'center').
        offset (pygame.Vector2): De verschuiving vanaf het ankerpunt.
    """

    def __init__(self, surface, anchor, offset, image_normal, image_hover):
        """
        Initialiseert de knop met afbeeldingen en positie-logica.

        Args:
            surface (pygame.Surface): De doelsurface.
            anchor (str): Attribuutnaam van een Rect (bijv. 'center', 'midbottom').
            offset (tuple): (x, y) verschuiving ten opzichte van het anker.
            image_normal (str/Path): Pad naar de standaard afbeelding.
            image_hover (str/Path): Pad naar de afbeelding tijdens hooveren.
        """
        self.surface = surface

        self.n_image = pygame.image.load(image_normal).convert_alpha()
        self.h_image = pygame.image.load(image_hover).convert_alpha()

        self.image = self.n_image
        self.rect = self.image.get_rect()

        self.anchor = anchor
        self.offset = pygame.Vector2(offset)

        self.update_position()

    def update_position(self):
        """Berekent de positie van de knop opnieuw op basis van het anker en de offset."""
        surface_rect = self.surface.get_rect()
        anchor_pos = getattr(surface_rect, self.anchor)
        setattr(self.rect, self.anchor, anchor_pos + self.offset)

    def update(self):
        """Controleert of de muis over de knop zweeft en past de afbeelding aan."""
        self.get_mouse_pos()
        if self.rect.collidepoint(self.mouse_scaled):
            self.image = self.h_image
        else:
            self.image = self.n_image

    def draw(self):
        """Tekent de huidige afbeelding van de knop op de surface."""
        self.surface.blit(self.image, self.rect)

    def is_pressed(self, event):
        """
        Controleert of er op de knop is geklikt tijdens een MOUSEBUTTONDOWN event.

        Args:
            event (pygame.event.Event): Het Pygame event om te controleren.

        Returns:
            bool: True als de linker muisknop op de knop is ingedrukt.
        """
        self.get_mouse_pos()
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(self.mouse_scaled)
        )

    def get_mouse_pos(self):
        """
        Schaalt de muispositie van de monitor-resolutie naar de interne game-resolutie.
        Dit is noodzakelijk voor correcte collision-detectie in fullscreen modus.
        """
        info = pygame.display.Info()
        scale_x = BASE_SCREEN_WIDTH / info.current_w
        scale_y = BASE_SCREEN_HEIGHT / info.current_h
        mouse_pos = pygame.mouse.get_pos()
        self.mouse_scaled = pygame.math.Vector2(mouse_pos[0] * scale_x, mouse_pos[1] * scale_y)


class Slider:
    """
    Een grafische schuif voor het aanpassen van waarden zoals volume.

    De slider geeft een genormaliseerde waarde tussen 0.0 en 1.0 terug op basis 
    van de positie van de knop (knob).
    """

    def __init__(self, surface, pos, width, knob_image, knob_hover):
        """
        Initialiseert de slider en zijn grenzen.

        Args:
            surface (pygame.Surface): De doelsurface.
            pos (tuple): De (x, y) positie van het midden van de slider-lijn.
            width (int): De totale breedte van de slider in pixels.
            knob_image (str/Path): Afbeelding voor de schuifknop.
            knob_hover (str/Path): Afbeelding voor de schuifknop tijdens hooveren.
        """
        self.surface = surface
        self.x, self.y = pos
        self.width = width

        #laad graphics van de slider in
        self.knob_normal = pygame.image.load(knob_image).convert_alpha() 
        self.knob_hover = pygame.image.load(knob_hover).convert_alpha()

        self.knob_image = self.knob_normal
        self.knob_rect = self.knob_image.get_rect(center=(self.x, self.y))

        self.dragging = False

        # Slider limieten
        self.min_x = self.x - width // 2
        self.max_x = self.x + width // 2

        # Waarde tussen 0 en 1
        self.value = 0.5
        self.update_knob_position()

    def update_knob_position(self):
        """Zet de visuele positie van de knop gelijk aan de interne waarde."""
        self.knob_rect.centerx = self.min_x + self.value * self.width
        self.knob_rect.centery = self.y

    def handle_event(self, event):
        """
        Beheert het slepen van de slider-knop.

        Args:
            event (pygame.event.Event): Muis-klik, loslaat of beweging events.
        """
        self.get_mouse_pos()
        mouse_pos = self.mouse_scaled
    
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.knob_rect.collidepoint(mouse_pos):
                self.dragging = True
    
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
    
        if event.type == pygame.MOUSEMOTION and self.dragging:
            new_x = max(self.min_x, min(self.max_x, mouse_pos.x))
            self.knob_rect.centerx = new_x
            self.value = (new_x - self.min_x) / self.width

    def update(self):
        """Update de hover-status van de slider-knop."""
        self.get_mouse_pos()
        if self.knob_rect.collidepoint(self.mouse_scaled):
            self.knob_image = self.knob_hover
        else:
            self.knob_image = self.knob_normal

    def get_mouse_pos(self):
        """Schaalt de muispositie naar de interne resolutie."""
        info = pygame.display.Info()
        scale_x = BASE_SCREEN_WIDTH / info.current_w
        scale_y = BASE_SCREEN_HEIGHT / info.current_h
        mouse_pos = pygame.mouse.get_pos()
        self.mouse_scaled = pygame.math.Vector2(mouse_pos[0] * scale_x, mouse_pos[1] * scale_y)

    def draw(self):
        """Tekent de slider-lijn en de knop op het scherm."""
        pygame.draw.line(self.surface, (200, 200, 200), (self.min_x, self.y), (self.max_x, self.y), 6)
        self.surface.blit(self.knob_image, self.knob_rect)

    def get_value(self):
        """Returns: float: De huidige waarde van de slider (0.0 tot 1.0)."""
        return self.value


class MainMenu:
    """
    Het hoofd menu van de game met navigatieknoppen.
    """

    def __init__(self, game):
        """
        Initialiseert de achtergrond, titel en menu-knoppen.

        Args:
            game (Game): Referentie naar het hoofd Game object voor state-wisselingen.
        """
        self.game = game
        self.display = game.game_surface

        buttons_path = BASE_DIR.parent / "graphics" / "buttons"
        other_images_path = BASE_DIR.parent / "graphics" / "other_images"

        self.bg = pygame.image.load(other_images_path / "test_mainmenu_bg.png").convert()
        self.bg = pygame.transform.scale(self.bg, (BASE_SCREEN_WIDTH, BASE_SCREEN_HEIGHT))
        self.title = pygame.image.load(other_images_path / 'title.png').convert_alpha()

        self.buttons = [
            Button(self.display, 'center', (0, 0), buttons_path / 'play01.png', buttons_path / 'play02.png'),
            Button(self.display, 'center', (0, 100), buttons_path / 'settings_1.png', buttons_path / 'settings_2.png'),
            Button(self.display, 'center', (0, 200), buttons_path / 'quit01.png', buttons_path / 'quit02.png')
        ]

        self.start_button = self.buttons[0]
        self.settings_button = self.buttons[1]
        self.quit_button = self.buttons[2]

    def handle_events(self, event):
        """Koppelt knop-klikken aan game-acties."""
        if self.start_button.is_pressed(event):
            self.game.set_state("game")
        elif self.settings_button.is_pressed(event):
            self.game.set_state("settings")
        elif self.quit_button.is_pressed(event):
            self.game.running = False

    def update(self):
        """Update de status van alle knoppen in het menu."""
        for button in self.buttons:
            button.update()

    def draw(self):
        """Tekent de achtergrond, titel en knoppen."""
        self.display.blit(self.bg, (0, 0))
        self.display.blit(self.title, (510, 70))
        for button in self.buttons:
            button.draw()


class SettingsMenu:
    """
    Menu voor spelinstellingen, zoals volume en het herstarten van het level.
    """

    def __init__(self, game):
        """
        Initialiseert de instellingen-UI, inclusief een semi-transparante overlay.

        Args:
            game (Game): Referentie naar de hoofd-game instantie.
        """
        self.game = game
        self.display = game.game_surface
        
        buttons_path = BASE_DIR.parent / "graphics" / "buttons"

        self.overlay = pygame.Surface((BASE_SCREEN_WIDTH, BASE_SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((50, 50, 50, 30))

        self.sizes = pygame.display.get_desktop_sizes()
        self.current_ratio_index = 0
        self.font = pygame.font.SysFont("arial", 28)

        self.buttons = [
            Button(self.display, 'center', (0, 200), buttons_path / 'back01.png', buttons_path / 'back02.png'),
            Button(self.display, 'center', (0, 100), buttons_path / 'restart01.png', buttons_path / 'restart02.png'),
            Slider(self.display, (650, 300), 300, buttons_path / 'knob01.png',  buttons_path / 'knob02.png')
        ]

        self.back_button = self.buttons[0]
        self.restart_button = self.buttons[1]
        self.music_volume_slider = self.buttons[2]

    def handle_events(self, event):
        """Verwerkt input voor de slider en de navigatieknoppen."""
        self.music_volume_slider.handle_event(event)

        if self.back_button.is_pressed(event):
            self.game.set_state(self.game.previous_state)
        elif self.restart_button.is_pressed(event):
            self.game.restart_level()
            self.game.set_state('menu')

    def update(self):
        """Update de knoppen en synchroniseert het volume met de slider-waarde."""
        for button in self.buttons:
            button.update()
        self.game.audio.set_volume(self.music_volume_slider.get_value())

    def draw(self):
        """Tekent de overlay, resolutie-informatie en de UI-elementen."""
        self.display.blit(self.overlay, (0, 0))

        text1 = self.font.render(f"Resolution: {self.sizes[self.current_ratio_index]}", True, (0, 200, 255))
        self.display.blit(text1, (120, 150))

        text2 = self.font.render(f"Volume: {int(self.music_volume_slider.value * 100)}%", True, (0, 100, 255))
        self.display.blit(text2, (580, 230))

        for button in self.buttons:
            button.draw()