import pygame


class AudioManager:
    def __init__(self, music_paths, volume=0.1):
        pygame.mixer.init()

        self.tracks = {}
        self.channels = {}

        for name, path in music_paths.items():
            sound = pygame.mixer.Sound(path)
            sound.set_volume(volume)
            self.tracks[name] = sound
            self.channels[name] = None

        self.current_track = None


    def play(self, track_name):

        # Pause currently playing track
        if self.current_track and self.channels[self.current_track]:
            self.channels[self.current_track].pause()

        # If this track already started before → resume it
        if self.channels[track_name]:
            self.channels[track_name].unpause()

        else:
            # First time playing
            self.channels[track_name] = self.tracks[track_name].play(loops=-1)

        self.current_track = track_name


    def pause(self):
        if self.current_track and self.channels[self.current_track]:
            self.channels[self.current_track].pause()


    def resume(self):
        if self.current_track and self.channels[self.current_track]:
            self.channels[self.current_track].unpause()


    def stop(self):
        if self.current_track and self.channels[self.current_track]:
            self.channels[self.current_track].stop()
            self.channels[self.current_track] = None
            self.current_track = None

    def play_sfx(self, sfx_name, volume=0.1):
        self.tracks[sfx_name].set_volume(volume)
        self.tracks[sfx_name].play()
