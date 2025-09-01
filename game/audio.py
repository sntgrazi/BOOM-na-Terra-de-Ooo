import pygame
import numpy as np
import math
import random

class AudioManager:
    def __init__(self):
        self.sample_rate = 22050
        self.is_muted = False
        self.background_music_playing = False

        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=2, buffer=512)
        
        self.sfx_channel = pygame.mixer.Channel(0)
        self.music_channel = pygame.mixer.Channel(1)
        
        self.custom_sounds = {}
        self.load_custom_sounds()
        
        print("🔊 Sistema de áudio inicializado")
    
    def load_custom_sounds(self):
        
        import os
        
        sound_files = {
            'bomb_place': 'sounds/client_public_sound_bomb_0.wav',
            'explosion': 'sounds/client_public_sound_blast_0.wav'
        }
        
        for sound_name, file_path in sound_files.items():
            try:
                if os.path.exists(file_path):
                    self.custom_sounds[sound_name] = pygame.mixer.Sound(file_path)
                    print(f"🔊 Som personalizado carregado: {sound_name} -> {file_path}")
                else:
                    print(f"⚠️ Arquivo de som não encontrado: {file_path}")
                    self.custom_sounds[sound_name] = None
            except Exception as e:
                print(f"❌ Erro ao carregar som {sound_name}: {e}")
                self.custom_sounds[sound_name] = None
    
    def generate_tone(self, frequency, duration, wave_type='sine', volume=0.5):
        frames = int(duration * self.sample_rate)
        arr = np.zeros(frames)
        
        for i in range(frames):
            t = float(i) / self.sample_rate
            
            if wave_type == 'sine':
                arr[i] = volume * math.sin(2 * math.pi * frequency * t)
            elif wave_type == 'square':
                arr[i] = volume * (1 if math.sin(2 * math.pi * frequency * t) > 0 else -1)
            elif wave_type == 'sawtooth':
                arr[i] = volume * (2 * (t * frequency - math.floor(t * frequency + 0.5)))
            elif wave_type == 'triangle':
                arr[i] = volume * (2 * abs(2 * (t * frequency - math.floor(t * frequency + 0.5))) - 1)

        fade_frames = min(frames // 20, 1000)
        for i in range(fade_frames):
            fade_factor = i / fade_frames
            arr[i] *= fade_factor
            arr[frames - 1 - i] *= fade_factor

        arr = (arr * 32767).astype(np.int16)

        stereo_arr = np.zeros((frames, 2), dtype=np.int16)
        stereo_arr[:, 0] = arr
        stereo_arr[:, 1] = arr
        
        return pygame.sndarray.make_sound(stereo_arr)
    
    def generate_noise(self, duration, volume=0.3):
        frames = int(duration * self.sample_rate)
        arr = np.random.uniform(-1, 1, frames) * volume
        
        fade_frames = frames // 4
        for i in range(fade_frames):
            fade_factor = 1 - (i / fade_frames)
            arr[frames - fade_frames + i] *= fade_factor
        
     
        arr = (arr * 32767).astype(np.int16)

        stereo_arr = np.zeros((frames, 2), dtype=np.int16)
        stereo_arr[:, 0] = arr
        stereo_arr[:, 1] = arr
        
        return pygame.sndarray.make_sound(stereo_arr)
    
    def generate_sweep(self, start_freq, end_freq, duration, volume=0.4):
       
        frames = int(duration * self.sample_rate)
        arr = np.zeros(frames)
        
        for i in range(frames):
            t = float(i) / self.sample_rate
            progress = i / frames
            frequency = start_freq + (end_freq - start_freq) * progress
            arr[i] = volume * math.sin(2 * math.pi * frequency * t)
        
     
        for i in range(frames):
            envelope = math.sin(math.pi * i / frames)  
            arr[i] *= envelope
  
        arr = (arr * 32767).astype(np.int16)
        

        stereo_arr = np.zeros((frames, 2), dtype=np.int16)
        stereo_arr[:, 0] = arr
        stereo_arr[:, 1] = arr
        
        return pygame.sndarray.make_sound(stereo_arr)
    
    def play_bomb_sound(self):
        
        if self.is_muted:
            return
        
        try:
            
            if self.custom_sounds.get('bomb_place'):
                self.sfx_channel.play(self.custom_sounds['bomb_place'])
                print("🔊 Tocando som personalizado da bomba")
            else:
                
                sound = self.generate_tone(150, 0.2, 'square', 0.3)
                self.sfx_channel.play(sound)
                print("🔊 Tocando som gerado da bomba")
        except Exception as e:
            print(f"❌ Erro ao tocar som da bomba: {e}")
    
    def play_explosion_sound(self):
        
        if self.is_muted:
            return
        
        try:
           
            if self.custom_sounds.get('explosion'):
                self.sfx_channel.play(self.custom_sounds['explosion'])
                print("💥 Tocando som personalizado da explosão")
            else:
              
                noise = self.generate_noise(0.5, 0.4)
                self.sfx_channel.play(noise)
                print("💥 Tocando som gerado da explosão")
        except Exception as e:
            print(f"❌ Erro ao tocar som da explosão: {e}")
    
    def play_powerup_sound(self):
       
        if self.is_muted:
            return
        
        try:
            
            sound = self.generate_sweep(440, 880, 0.3, 0.3)
            self.sfx_channel.play(sound)
        except Exception as e:
            print(f"Erro ao tocar som do power-up: {e}")
    
    def play_game_over_sound(self):
       
        if self.is_muted:
            return
        
        try:
           
            sound = self.generate_sweep(440, 110, 1.0, 0.4)
            self.sfx_channel.play(sound)
        except Exception as e:
            print(f"Erro ao tocar som de game over: {e}")
    
    def play_victory_sound(self):
      
        if self.is_muted:
            return
        
        try:
          
            sound = self.generate_sweep(440, 880, 0.8, 0.4)
            self.sfx_channel.play(sound)
        except Exception as e:
            print(f"Erro ao tocar som de vitória: {e}")
    
    def play_menu_sound(self):
        
        if self.is_muted:
            return
        
        try:
         
            sound = self.generate_tone(800, 0.1, 'sine', 0.2)
            self.sfx_channel.play(sound)
        except Exception as e:
            print(f"Erro ao tocar som do menu: {e}")
    
    def start_background_music(self):
      
        if self.is_muted or self.background_music_playing:
            return
        
        try:
          
            self.background_music_playing = True
            print("🎵 Música de fundo iniciada")
        except Exception as e:
            print(f"Erro ao iniciar música de fundo: {e}")
    
    def stop_background_music(self):
        
        try:
            self.music_channel.stop()
            self.background_music_playing = False
            print("🎵 Música de fundo parada")
        except Exception as e:
            print(f"Erro ao parar música de fundo: {e}")
    
    def toggle_mute(self):
        
        self.is_muted = not self.is_muted
        
        if self.is_muted:
            self.stop_background_music()
            self.sfx_channel.stop()
            print("🔇 Áudio mutado")
        else:
            print("🔊 Áudio ativado")
        
        return not self.is_muted  
    
    def stop_all_sounds(self):
        
        try:
            self.sfx_channel.stop()
            self.stop_background_music()
        except Exception as e:
            print(f"Erro ao parar todos os sons: {e}")
    
    def cleanup(self):
        
        self.stop_all_sounds()
        print("🔊 Sistema de áudio finalizado")


