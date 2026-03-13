import pygame


class AudioManager:
    """
    Beheert muziek en geluidseffecten met pygame.mixer.
    """

    def __init__(self, music_paths, volume=0.5):
        """
        Initialiseert de AudioManager.

        music_paths : dict
            Dictionary met namen van tracks en hun bestandspaden.
        volume : float
            Standaard volume (0.0 – 1.0).
        """
        pygame.mixer.init()

        self.volume = volume
        self.tracks = {}
        self.channels = {}

        for name, path in music_paths.items():
            sound = pygame.mixer.Sound(path)
            sound.set_volume(self.volume)
            self.tracks[name] = sound
            self.channels[name] = None

        self.current_track = None

    def set_volume(self, volume):
        """
        Verandert het volume van alle tracks.
        """
        self.volume = volume
    
        for sound in self.tracks.values():
            sound.set_volume(self.volume)

    def play(self, track_name):
        """
        Speelt een track af. De huidige track wordt gepauzeerd.
        Als de track al eerder gestart was, wordt deze hervat.
        """

        if self.current_track and self.channels[self.current_track]:
            self.channels[self.current_track].pause()

        if self.channels[track_name]:
            self.channels[track_name].unpause()
        else:
            self.channels[track_name] = self.tracks[track_name].play(loops=-1)

        self.current_track = track_name


    def pause(self):
        """
        Pauzeert de huidige track.
        """
        if self.current_track and self.channels[self.current_track]:
            self.channels[self.current_track].pause()


    def resume(self):
        """
        Hervat de gepauzeerde track.
        """
        if self.current_track and self.channels[self.current_track]:
            self.channels[self.current_track].unpause()


    def stop(self):
        """
        Stopt de huidige track volledig.
        """
        if self.current_track and self.channels[self.current_track]:
            self.channels[self.current_track].stop()
            self.channels[self.current_track] = None
            self.current_track = None


    def play_sfx(self, sfx_name, volume=0.1):
        """
        Speelt een geluidseffect één keer af.
        """
        self.tracks[sfx_name].set_volume(volume)
        self.tracks[sfx_name].play()