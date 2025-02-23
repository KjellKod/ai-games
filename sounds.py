import pygame
import math
import array

class PacmanSounds:
    def __init__(self):
        pygame.mixer.init()
        
        # Create simple eating sound (a short beep)
        self.eating_sound = self._create_eating_sound()
        self.eating_sound.set_volume(0.3)
        
        # Create simple walking sound (alternating beeps)
        self.walking_sound = self._create_walking_sound()
        self.walking_sound.set_volume(0.2)
        
        # Create death sound
        self.death_sound = self._create_death_sound()
        self.death_sound.set_volume(0.4)
        
    def _create_eating_sound(self):
        """Create a simple 'wakka' sound"""
        sound = pygame.mixer.Sound(self._generate_sound_array(
            frequency=1200,
            duration=100,
            volume=0.3
        ))
        return sound
    
    def _create_walking_sound(self):
        """Create a simple walking sound"""
        sound = pygame.mixer.Sound(self._generate_sound_array(
            frequency=800,
            duration=50,
            volume=0.2
        ))
        return sound
    
    def _create_death_sound(self):
        """Create a descending sound for death"""
        duration = 500  # milliseconds
        sample_rate = 44100
        num_samples = int(duration * sample_rate / 1000)
        
        sound_array = array.array('B')
        for i in range(num_samples):
            # Frequency decreases over time from 1500Hz to 200Hz
            t = i / num_samples
            freq = 1500 - (1300 * t)
            value = int(128.0 + 127.0 * math.sin(2.0 * math.pi * freq * i / sample_rate))
            sound_array.append(value)
            sound_array.append(value)
        
        return pygame.mixer.Sound(sound_array)
    
    def _generate_sound_array(self, frequency, duration, volume=0.3):
        """Generate a simple sine wave sound"""
        sample_rate = 44100
        num_samples = int(duration * sample_rate / 1000)
        sound_array = array.array('B')
        
        for i in range(num_samples):
            # Generate value between 0 and 255
            value = int(128.0 + 127.0 * volume * math.sin(2.0 * math.pi * frequency * i / sample_rate))
            sound_array.append(value)
            sound_array.append(value)
        
        return sound_array
    
    def play_eat(self):
        """Play eating sound"""
        self.eating_sound.play()
    
    def play_walk(self):
        """Play walking sound"""
        self.walking_sound.play()
    
    def play_death(self):
        """Play death sound"""
        self.death_sound.play()
