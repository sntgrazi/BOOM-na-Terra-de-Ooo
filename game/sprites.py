import pygame
import os
import random
from .constants import *

class SpriteManager:
    def __init__(self):
        self.images = {}
        self.images_loaded = {}
        self.load_images()
    
    def load_images(self):
        self.load_finn_directional_sprites()
        self.load_jake_directional_sprites()
        self.load_marceline_directional_sprites()
        self.load_princesa_directional_sprites()
        self.load_fire_princess_directional_sprites()
        self.load_jellybean_princess_directional_sprites()
        self.create_basic_sprites()
        self.load_character_bombs()
        self.load_powerup_sprites()
        self.load_background_map()
    
    def scale_sprite_proportional(self, sprite, target_size):
        original_width, original_height = sprite.get_size()
        target_width, target_height = target_size, target_size
        
        if original_width == target_width and original_height == target_height:
            return sprite
        
        scale_x = target_width / original_width
        scale_y = target_height / original_height
        scale = min(scale_x, scale_y)
        
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        
        if scale >= 1.0:
            scaled_sprite = pygame.transform.smoothscale(sprite, (new_width, new_height))
        elif scale >= 0.5:
            scaled_sprite = pygame.transform.scale(sprite, (new_width, new_height))
        else:
            scaled_sprite = pygame.transform.smoothscale(sprite, (new_width, new_height))
            scaled_sprite = self.apply_sharpening_filter(scaled_sprite)
        
        if new_width != target_width or new_height != target_height:
            centered_surface = pygame.Surface((target_width, target_height), pygame.SRCALPHA)
            centered_surface = centered_surface.convert_alpha()
            
            x_offset = (target_width - new_width) // 2
            y_offset = (target_height - new_height) // 2
            centered_surface.blit(scaled_sprite, (x_offset, y_offset))
            
            return centered_surface
        
        return scaled_sprite
    
    def apply_sharpening_filter(self, sprite):
        try:
            width, height = sprite.get_size()
            if width > 10 and height > 10:
                pass
        except:
            pass
        
        return sprite
    
    def load_finn_directional_sprites(self):
        finn_sprites = {
            'idle': {
                'down': "images/finn_idle.png",
                'up': "images/finn_idle_up.png", 
                'left': "images/finn_idle_left.png",
                'right': "images/finn_idle_right.png"
            },
            'walk': {
                'down': ["images/finn_walk_down_01.png", "images/finn_walk_down_02.png"],
                'up': ["images/finn_walk_up_01.png", "images/finn_walk_up_02.png"],
                'left': ["images/finn_walk_left_01.png", "images/finn_walk_left_02.png"],
                'right': ["images/finn_walk_right_01.png", "images/finn_walk_right_02.png"]
            }
        }
        
        loaded_sprites = {
            'idle': {},
            'walk': {},
            'current_direction': 'down',
            'current_state': 'idle',
            'current_frame': 0,
            'animation_speed': 8
        }
        
        for direction, path in finn_sprites['idle'].items():
            if os.path.exists(path):
                try:
                    sprite = pygame.image.load(path).convert_alpha()
                    sprite = self.scale_sprite_proportional(sprite, TILE_SIZE)
                    loaded_sprites['idle'][direction] = sprite
                    print(f"✅ Finn idle {direction} carregado: {path}")
                except Exception as e:
                    print(f"❌ Erro ao carregar Finn idle {direction}: {e}")
            else:
                print(f"⚠️ Sprite não encontrado: {path}")
        
        for direction, paths in finn_sprites['walk'].items():
            loaded_sprites['walk'][direction] = []
            for i, path in enumerate(paths):
                if os.path.exists(path):
                    try:
                        sprite = pygame.image.load(path).convert_alpha()
                        sprite = self.scale_sprite_proportional(sprite, TILE_SIZE)
                        loaded_sprites['walk'][direction].append(sprite)
                        print(f"✅ Finn walk {direction} frame {i+1} carregado: {path}")
                    except Exception as e:
                        print(f"❌ Erro ao carregar Finn walk {direction} frame {i+1}: {e}")
                else:
                    print(f"⚠️ Sprite não encontrado: {path}")
        
        total_loaded = (len(loaded_sprites['idle']) + 
                       sum(len(frames) for frames in loaded_sprites['walk'].values()))
        
        if total_loaded > 0:
            self.images[Characters.FINN] = loaded_sprites
            self.images_loaded[Characters.FINN] = True
            print(f"✅ Finn sprites direcionais configurados: {total_loaded} sprites carregados")
        else:
            self.images_loaded[Characters.FINN] = False
            print("❌ Nenhum sprite do Finn foi carregado")
    
    def load_jake_directional_sprites(self):
        jake_sprites = {
            'idle': {
                'down': "images/jake_idle_down.png",
                'up': "images/jake_idle_up.png", 
                'left': "images/jake_idle_left.png",
                'right': "images/jake_idle_right.png"
            },
            'walk': {
                'down': ["images/jake_walk_down_01.png", "images/jake_walk_down_02.png"],
                'up': ["images/jake_walk_up_01.png", "images/jake_walk_up_02.png"],
                'left': ["images/jake_walk_left_01.png", "images/jake_walk_left_02.png"],
                'right': ["images/jake_walk_right_01.png", "images/jake_walk_right_02.png"]
            }
        }
        
        loaded_sprites = {
            'idle': {},
            'walk': {},
            'current_direction': 'down',
            'current_state': 'idle',
            'current_frame': 0,
            'animation_speed': 8
        }
        
        for direction, path in jake_sprites['idle'].items():
            if os.path.exists(path):
                try:
                    sprite = self.load_jake_sprite_optimized(path)
                    loaded_sprites['idle'][direction] = sprite
                    print(f"✅ Jake idle {direction} carregado (otimizado): {path}")
                except Exception as e:
                    print(f"❌ Erro ao carregar Jake idle {direction}: {e}")
            else:
                print(f"⚠️ Sprite não encontrado: {path}")
        
        for direction, paths in jake_sprites['walk'].items():
            loaded_sprites['walk'][direction] = []
            for i, path in enumerate(paths):
                if os.path.exists(path):
                    try:
                        sprite = self.load_jake_sprite_optimized(path)
                        loaded_sprites['walk'][direction].append(sprite)
                        print(f"✅ Jake walk {direction} frame {i+1} carregado (otimizado): {path}")
                    except Exception as e:
                        print(f"❌ Erro ao carregar Jake walk {direction} frame {i+1}: {e}")
                else:
                    print(f"⚠️ Sprite não encontrado: {path}")
        
        total_loaded = (len(loaded_sprites['idle']) + 
                       sum(len(frames) for frames in loaded_sprites['walk'].values()))
        
        if total_loaded > 0:
            self.images[Characters.JAKE] = loaded_sprites
            self.images_loaded[Characters.JAKE] = True
            print(f"✅ Jake sprites direcionais configurados: {total_loaded} sprites carregados")
        else:
            self.images_loaded[Characters.JAKE] = False
            print("❌ Nenhum sprite do Jake foi carregado")
    
    def load_jake_sprite_optimized(self, path):
        sprite = pygame.image.load(path).convert_alpha()
        
        original_width, original_height = sprite.get_size()
        
        if original_width <= 30 and original_height <= 35:
            scale_x = TILE_SIZE / original_width
            scale_y = TILE_SIZE / original_height
            scale = min(scale_x, scale_y)
            
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            
            sprite = pygame.transform.scale(sprite, (new_width, new_height))
            
            if new_width != TILE_SIZE or new_height != TILE_SIZE:
                centered_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                centered_surface = centered_surface.convert_alpha()
                
                x_offset = (TILE_SIZE - new_width) // 2
                y_offset = (TILE_SIZE - new_height) // 2
                centered_surface.blit(sprite, (x_offset, y_offset))
                
                return centered_surface
                
        else:
            sprite = self.scale_sprite_proportional(sprite, TILE_SIZE)
        
        return sprite
    
    def load_marceline_directional_sprites(self):
        marceline_sprites = {
            'idle': {
                'down': "images/marceline_idle_down.png",
                'up': "images/marceline_idle_up.png", 
                'left': "images/marceline_idle_left.png",
                'right': "images/marceline_idle_right.png"
            },
            'walk': {
                'down': ["images/marceline_walk_down_01.png", "images/marceline_walk_down_02.png"],
                'up': ["images/marceline_walk_up_01.png", "images/marceline_walk_up_02.png"],
                'left': ["images/marceline_walk_left_01.png", "images/marceline_walk_left_02.png"],
                'right': ["images/marceline_walk_right_01.png", "images/marceline_walk_right_02.png"]
            }
        }
        
        loaded_sprites = {
            'idle': {},
            'walk': {},
            'current_direction': 'down',
            'current_state': 'idle',
            'current_frame': 0,
            'animation_speed': 8
        }
        
        for direction, path in marceline_sprites['idle'].items():
            if os.path.exists(path):
                try:
                    sprite = pygame.image.load(path).convert_alpha()
                    sprite = self.scale_sprite_proportional(sprite, TILE_SIZE)
                    loaded_sprites['idle'][direction] = sprite
                    print(f"✅ Marceline idle {direction} carregado: {path}")
                except Exception as e:
                    print(f"❌ Erro ao carregar Marceline idle {direction}: {e}")
            else:
                print(f"⚠️ Sprite não encontrado: {path}")
        
        for direction, paths in marceline_sprites['walk'].items():
            loaded_sprites['walk'][direction] = []
            for i, path in enumerate(paths):
                if os.path.exists(path):
                    try:
                        sprite = pygame.image.load(path).convert_alpha()
                        sprite = self.scale_sprite_proportional(sprite, TILE_SIZE)
                        loaded_sprites['walk'][direction].append(sprite)
                        print(f"✅ Marceline walk {direction} frame {i+1} carregado: {path}")
                    except Exception as e:
                        print(f"❌ Erro ao carregar Marceline walk {direction} frame {i+1}: {e}")
                else:
                    print(f"⚠️ Sprite não encontrado: {path}")
        
        total_loaded = (len(loaded_sprites['idle']) + 
                       sum(len(frames) for frames in loaded_sprites['walk'].values()))
        
        if total_loaded > 0:
            self.images[Characters.MARCELINE] = loaded_sprites
            self.images_loaded[Characters.MARCELINE] = True
            print(f"✅ Marceline sprites direcionais configurados: {total_loaded} sprites carregados")
        else:
            self.images_loaded[Characters.MARCELINE] = False
            print("❌ Nenhum sprite da Marceline foi carregado")
    
    def load_princesa_directional_sprites(self):
        princesa_sprites = {
            'idle': {
                'down': "images/princess_lump_idle_down.png",
                'up': "images/princess_lump_idle_up.png", 
                'left': "images/princess_lump_idle_left.png",
                'right': "images/princess_lump_idle_right.png"
            },
            'walk': {
                'down': ["images/princess_lump_walk_down_01.png", "images/princess_lump_walk_down_02.png"],
                'up': ["images/princess_lump_walk_up_01.png", "images/princess_lump_walk_up_02.png"],
                'left': ["images/princess_lump_walk_left_01.png", "images/princess_lump_walk_left_02.png"],
                'right': ["images/princess_lump_walk_right_01.png", "images/princess_lump_walk_right_02.png"]
            }
        }
        
        loaded_sprites = {
            'idle': {},
            'walk': {},
            'current_direction': 'down',
            'current_state': 'idle',
            'current_frame': 0,
            'animation_speed': 8
        }
        
        for direction, path in princesa_sprites['idle'].items():
            if os.path.exists(path):
                try:
                    sprite = pygame.image.load(path).convert_alpha()
                    sprite = self.scale_sprite_proportional(sprite, TILE_SIZE)
                    loaded_sprites['idle'][direction] = sprite
                    print(f"✅ Princesa idle {direction} carregado: {path}")
                except Exception as e:
                    print(f"❌ Erro ao carregar Princesa idle {direction}: {e}")
            else:
                print(f"⚠️ Sprite não encontrado: {path}")
        
        for direction, paths in princesa_sprites['walk'].items():
            loaded_sprites['walk'][direction] = []
            for i, path in enumerate(paths):
                if os.path.exists(path):
                    try:
                        sprite = pygame.image.load(path).convert_alpha()
                        sprite = self.scale_sprite_proportional(sprite, TILE_SIZE)
                        loaded_sprites['walk'][direction].append(sprite)
                        print(f"✅ Princesa walk {direction} frame {i+1} carregado: {path}")
                    except Exception as e:
                        print(f"❌ Erro ao carregar Princesa walk {direction} frame {i+1}: {e}")
                else:
                    print(f"⚠️ Sprite não encontrado: {path}")
        
        total_loaded = (len(loaded_sprites['idle']) + 
                       sum(len(frames) for frames in loaded_sprites['walk'].values()))
        
        if total_loaded > 0:
            self.images[Characters.PRINCESS_LUMP] = loaded_sprites
            self.images_loaded[Characters.PRINCESS_LUMP] = True
            print(f"✅ Princesa sprites direcionais configurados: {total_loaded} sprites carregados")
        else:
            self.images_loaded[Characters.PRINCESS_LUMP] = False
            print("❌ Nenhum sprite da Princesa foi carregado")
    
    def load_fire_princess_directional_sprites(self):
        fire_princess_sprites = {
            'idle': {
                'down': "images/fire_princess_idle_down.png",
                'up': "images/fire_princess_idle_up.png", 
                'left': "images/fire_princess_idle_left.png",
                'right': "images/fire_princess_idle_right.png"
            },
            'walk': {
                'down': ["images/fire_princess_walk_down_01.png", "images/fire_princess_walk_down_02.png"],
                'up': ["images/fire_princess_walk_up_01.png", "images/fire_princess_walk_up_02.png"],
                'left': ["images/fire_princess_walk_left_01.png", "images/fire_princess_walk_left_02.png"],
                'right': ["images/fire_princess_walk_right_01.png", "images/fire_princess_walk_right_02.png"]
            }
        }
        
        loaded_sprites = {
            'idle': {},
            'walk': {},
            'current_direction': 'down',
            'current_state': 'idle',
            'current_frame': 0,
            'animation_speed': 8
        }
        
        for direction, path in fire_princess_sprites['idle'].items():
            if os.path.exists(path):
                try:
                    sprite = pygame.image.load(path).convert_alpha()
                    sprite = self.scale_sprite_proportional(sprite, TILE_SIZE)
                    loaded_sprites['idle'][direction] = sprite
                    print(f"✅ Fire Princess idle {direction} carregado: {path}")
                except Exception as e:
                    print(f"❌ Erro ao carregar Fire Princess idle {direction}: {e}")
            else:
                print(f"⚠️ Sprite não encontrado: {path}")
        
        for direction, paths in fire_princess_sprites['walk'].items():
            loaded_sprites['walk'][direction] = []
            for i, path in enumerate(paths):
                if os.path.exists(path):
                    try:
                        sprite = pygame.image.load(path).convert_alpha()
                        sprite = self.scale_sprite_proportional(sprite, TILE_SIZE)
                        loaded_sprites['walk'][direction].append(sprite)
                        print(f"✅ Fire Princess walk {direction} frame {i+1} carregado: {path}")
                    except Exception as e:
                        print(f"❌ Erro ao carregar Fire Princess walk {direction} frame {i+1}: {e}")
                else:
                    print(f"⚠️ Sprite não encontrado: {path}")
        
        total_loaded = (len(loaded_sprites['idle']) + 
                       sum(len(frames) for frames in loaded_sprites['walk'].values()))
        
        if total_loaded > 0:
            self.images[Characters.FIRE_PRINCESS] = loaded_sprites
            self.images_loaded[Characters.FIRE_PRINCESS] = True
            print(f"✅ Fire Princess sprites direcionais configurados: {total_loaded} sprites carregados")
        else:
            self.images_loaded[Characters.FIRE_PRINCESS] = False
            print("❌ Nenhum sprite da Fire Princess foi carregado")
    
    def load_jellybean_princess_directional_sprites(self):
        jellybean_princess_sprites = {
            'idle': {
                'down': "images/jellybean_princess_idle_down.png",
                'up': "images/jellybean_princess_idle_up.png", 
                'left': "images/jellybean_princess_idle_left.png",
                'right': "images/jellybean_princess_idle_right.png"
            },
            'walk': {
                'down': ["images/jellybean_princess_walk_down_01.png", "images/jellybean_princess_walk_down_02.png"],
                'up': ["images/jellybean_princess_walk_up_01.png", "images/jellybean_princess_walk_up_02.png"],
                'left': ["images/jellybean_princess_walk_left_01.png", "images/jellybean_princess_walk_left_02.png"],
                'right': ["images/jellybean_princess_walk_right_01.png", "images/jellybean_princess_walk_right_02.png"]
            }
        }
        
        loaded_sprites = {
            'idle': {},
            'walk': {},
            'current_direction': 'down',
            'current_state': 'idle',
            'current_frame': 0,
            'animation_speed': 8
        }
        
        for direction, path in jellybean_princess_sprites['idle'].items():
            if os.path.exists(path):
                try:
                    sprite = pygame.image.load(path).convert_alpha()
                    sprite = self.scale_sprite_proportional(sprite, TILE_SIZE)
                    loaded_sprites['idle'][direction] = sprite
                    print(f"✅ Jellybean Princess idle {direction} carregado: {path}")
                except Exception as e:
                    print(f"❌ Erro ao carregar Jellybean Princess idle {direction}: {e}")
            else:
                print(f"⚠️ Sprite não encontrado: {path}")
        
        for direction, paths in jellybean_princess_sprites['walk'].items():
            loaded_sprites['walk'][direction] = []
            for i, path in enumerate(paths):
                if os.path.exists(path):
                    try:
                        sprite = pygame.image.load(path).convert_alpha()
                        sprite = self.scale_sprite_proportional(sprite, TILE_SIZE)
                        loaded_sprites['walk'][direction].append(sprite)
                        print(f"✅ Jellybean Princess walk {direction} frame {i+1} carregado: {path}")
                    except Exception as e:
                        print(f"❌ Erro ao carregar Jellybean Princess walk {direction} frame {i+1}: {e}")
                else:
                    print(f"⚠️ Sprite não encontrado: {path}")
        
        total_loaded = (len(loaded_sprites['idle']) + 
                       sum(len(frames) for frames in loaded_sprites['walk'].values()))
        
        if total_loaded > 0:
            self.images[Characters.JELLYBEAN_PRINCESS] = loaded_sprites
            self.images_loaded[Characters.JELLYBEAN_PRINCESS] = True
            print(f"✅ Jellybean Princess sprites direcionais configurados: {total_loaded} sprites carregados")
        else:
            self.images_loaded[Characters.JELLYBEAN_PRINCESS] = False
            print("❌ Nenhum sprite da Jellybean Princess foi carregado")
    
    def load_princess_sprite_optimized(self, path, princess_name):
        sprite = pygame.image.load(path).convert_alpha()
        
        sprite = self.scale_sprite_proportional(sprite, TILE_SIZE)
        
        original_width, original_height = pygame.image.load(path).get_size()
        new_width, new_height = sprite.get_size()
        
        print(f"✅ {princess_name} - Tamanho original: {original_width}x{original_height}, Novo: {new_width}x{new_height} (TILE_SIZE={TILE_SIZE})")
        
        return sprite
    
    def load_character_bombs(self):
        bomb_files = {
            Characters.FINN: "images/bomba_finn.png",
            Characters.JAKE: "images/bomb_jake.png", 
            Characters.MARCELINE: "images/bomba_marceline.png",
            Characters.PRINCESS_LUMP: "images/bomba_princess_lump.png",
            Characters.FIRE_PRINCESS: "images/bomba_fire_princess.png",
            Characters.JELLYBEAN_PRINCESS: "images/bomba_princess_jellybean.png"
        }
        
        self.character_bombs = {}
        
        for character, bomb_path in bomb_files.items():
            if os.path.exists(bomb_path):
                try:
                    bomb_sprite = pygame.image.load(bomb_path).convert_alpha()
                    bomb_sprite = self.scale_sprite_proportional(bomb_sprite, TILE_SIZE)
                    
                    self.character_bombs[character] = bomb_sprite
                    print(f"✅ Bomba do {Characters.NAMES.get(character, character)} carregada: {bomb_path}")
                    
                except Exception as e:
                    print(f"❌ Erro ao carregar bomba do {Characters.NAMES.get(character, character)}: {e}")
                    self.character_bombs[character] = None
            else:
                print(f"⚠️ Bomba não encontrada para {Characters.NAMES.get(character, character)}: {bomb_path}")
                self.character_bombs[character] = None
        
        print(f"✅ {len([b for b in self.character_bombs.values() if b is not None])} bombas de personagem carregadas")

    def load_powerup_sprites(self):
        powerup_files = {
            "powerup_bomb": "images/power_up_extra_bomb.png",
            "powerup_range": "images/power_up_fire_power.png", 
            "powerup_speed": "images/power_up_speed.png"
        }
        
        for powerup_name, powerup_path in powerup_files.items():
            if os.path.exists(powerup_path):
                try:
                    powerup_sprite = pygame.image.load(powerup_path).convert_alpha()
                    powerup_sprite = self.scale_sprite_proportional(powerup_sprite, TILE_SIZE)
                    
                    self.images[powerup_name] = {'default': powerup_sprite}
                    self.images_loaded[powerup_name] = True
                    print(f"✅ Power-up {powerup_name} carregado: {powerup_path}")
                    
                except Exception as e:
                    print(f"❌ Erro ao carregar power-up {powerup_name}: {e}")
                    self.images_loaded[powerup_name] = False
            else:
                print(f"⚠️ Power-up não encontrado: {powerup_path}")
                self.images_loaded[powerup_name] = False
        
        print(f"✅ {len([name for name in powerup_files.keys() if self.images_loaded.get(name, False)])} sprites de power-up carregadas")

    def load_background_map(self):
        self.map_themes = {}
        self.current_theme = "default"
        
        self.load_map_theme("default", {
            'background': "images/mapa.png",
            'wall': "images/bloco-estrutural.png", 
            'brick': "images/bloco-destrutivel.png"
        })
        
        self.load_map_theme("candy", {
            'background': "images/mapa_reino_doce.png",
            'wall': "images/bloco-estrutural-reino-doce.png",
            'brick': "images/bloco-destrutivel-reino-doce.png"
        })
        
        self.load_map_theme("fire", {
            'background': "images/mapa-reino-fogo.png",
            'wall': "images/bloco-estrutural-reino-fogo.png",
            'brick': "images/bloco-destrutivel-reino-fogo.png"
        })
        
        self.set_map_theme("default")
        
        self.generate_simple_collision_grid()
    
    def load_map_theme(self, theme_name, theme_paths):
        theme_data = {}
        
        background_path = theme_paths['background']
        if os.path.exists(background_path):
            try:
                from .constants import SCREEN_WIDTH, SCREEN_HEIGHT
                map_image = pygame.image.load(background_path)
                theme_data['background'] = pygame.transform.scale(map_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                print(f"✅ Fundo do tema '{theme_name}' carregado: {background_path}")
            except Exception as e:
                print(f"❌ Erro ao carregar fundo do tema '{theme_name}': {e}")
                theme_data['background'] = None
        else:
            print(f"⚠️ Fundo do tema '{theme_name}' não encontrado: {background_path}")
            theme_data['background'] = None
        
        wall_path = theme_paths['wall']
        if os.path.exists(wall_path):
            try:
                wall_image = pygame.image.load(wall_path).convert_alpha()
                theme_data['wall'] = self.scale_sprite_proportional(wall_image, TILE_SIZE)
                print(f"✅ Blocos estruturais do tema '{theme_name}' carregados: {wall_path}")
            except Exception as e:
                print(f"❌ Erro ao carregar blocos estruturais do tema '{theme_name}': {e}")
                theme_data['wall'] = None
        else:
            print(f"⚠️ Blocos estruturais do tema '{theme_name}' não encontrados: {wall_path}")
            theme_data['wall'] = None
        
        brick_path = theme_paths['brick']
        if os.path.exists(brick_path):
            try:
                brick_image = pygame.image.load(brick_path).convert_alpha()
                theme_data['brick'] = self.scale_sprite_proportional(brick_image, TILE_SIZE)
                print(f"✅ Blocos destrutíveis do tema '{theme_name}' carregados: {brick_path}")
            except Exception as e:
                print(f"❌ Erro ao carregar blocos destrutíveis do tema '{theme_name}': {e}")
                theme_data['brick'] = None
        else:
            print(f"⚠️ Blocos destrutíveis do tema '{theme_name}' não encontrados: {brick_path}")
            theme_data['brick'] = None
        
        self.map_themes[theme_name] = theme_data
    
    def set_map_theme(self, theme_name):
        if theme_name in self.map_themes:
            self.current_theme = theme_name
            theme_data = self.map_themes[theme_name]
            
            self.background_map = theme_data['background']
            
            if theme_data['wall']:
                self.images['wall'] = {'default': theme_data['wall']}
                self.images_loaded['wall'] = True
            
            if theme_data['brick']:
                self.images['brick'] = {'default': theme_data['brick']}
                self.images_loaded['brick'] = True
            
            if theme_data['background']:
                self.images['background_map'] = {'default': theme_data['background']}
                self.images_loaded['background_map'] = True
            
            print(f"🎨 Tema de mapa alterado para: {theme_name}")
            return True
        else:
            print(f"❌ Tema '{theme_name}' não encontrado!")
            return False
    
    def get_theme_for_level(self, level):
        if level % 3 == 1:
            return "default"
        elif level % 3 == 2:
            return "candy"
        else:
            return "fire"
    
    def generate_simple_collision_grid(self):
        from .constants import TILE_SIZE, COLS, ROWS
        
        self.collision_grid = []
        
        print("🗺️ Gerando grid de colisão no estilo BOOM clássico...")
        
        for row in range(ROWS):
            collision_row = []
            for col in range(COLS):
                is_border = (col == 0 or col == COLS-1 or row == 0 or row == ROWS-1)
                is_structural_position = (col % 2 == 1 and row % 2 == 1)
                
                is_spawn_area = (
                    (col <= 2 and row <= 2) or  
                    (col >= COLS-3 and row <= 2) or
                    (col <= 2 and row >= ROWS-3) or
                    (col >= COLS-3 and row >= ROWS-3)
                )
                
                if is_border:
                    collision_row.append(2)
                elif is_spawn_area:
                    if is_structural_position and not (
                        (col == 1 and row == 1) or (col == COLS-2 and row == 1) or
                        (col == 1 and row == ROWS-2) or (col == COLS-2 and row == ROWS-2)
                    ):
                        collision_row.append(2)
                    else:
                        collision_row.append(0)
                elif is_structural_position:
                    collision_row.append(2)
                else:
                    if random.random() < 0.6:
                        collision_row.append(1)
                    else:
                        collision_row.append(0)
            
            self.collision_grid.append(collision_row)
        
        print(f"✅ Grid de colisão gerado: {COLS}x{ROWS}")
        print("🎯 Cantos reservados para spawns:")
        print(f"   🟩 Superior esquerdo (player): (1-2, 1-2)")
        print(f"   🟦 Superior direito (inimigo): ({COLS-3}-{COLS-2}, 1-2)")
        print(f"   🟨 Inferior esquerdo (inimigo): (1-2, {ROWS-3}-{ROWS-2})")
        print(f"   🟪 Inferior direito (inimigo): ({COLS-3}-{COLS-2}, {ROWS-3}-{ROWS-2})")
        
        print("🗺️ Amostra do grid de colisão:")
        for i in range(min(8, ROWS)):
            row_str = ""
            for j in range(min(15, COLS)):
                if self.collision_grid[i][j] == 0:
                    row_str += "·"
                elif self.collision_grid[i][j] == 1:
                    row_str += "▓"
                else:
                    row_str += "█"
            print(f"   Linha {i}: {row_str}")
        print("   (· = livre, ▓ = destrutível, █ = estrutural)")
    
    def analyze_map_collisions(self, map_surface):
        from .constants import TILE_SIZE, COLS, ROWS
        
        self.collision_grid = []
        
        print("🔍 Analisando mapa para colisões...")
        
        for row in range(ROWS):
            collision_row = []
            for col in range(COLS):
                pixel_x = col * TILE_SIZE + TILE_SIZE // 2
                pixel_y = row * TILE_SIZE + TILE_SIZE // 2
                
                if (pixel_x < map_surface.get_width() and 
                    pixel_y < map_surface.get_height()):
                    
                    color = map_surface.get_at((pixel_x, pixel_y))
                    r, g, b = color[:3]
                    
                    brightness = (r + g + b) / 3
                    
                    is_light_green_floor = (g > 180 and brightness > 150 and r > 120 and b > 120)
                    
                    is_dark_green_block = (g > 140 and g < 180 and brightness < 150)
                    
                    is_very_dark = brightness < 50
                    
                    is_walkable = is_light_green_floor and not is_dark_green_block and not is_very_dark
                    
                    collision_row.append(0 if is_walkable else 1)
                    
                    if row < 5 and col < 8:
                        print(f"   ({col},{row}): RGB({r},{g},{b}) bright:{brightness:.1f} light_floor:{is_light_green_floor} dark_block:{is_dark_green_block} -> {'walkable' if is_walkable else 'blocking'}")
                        
                else:
                    collision_row.append(1)
            
            self.collision_grid.append(collision_row)
        
        print(f"✅ Grid de colisão gerado: {COLS}x{ROWS}")
        
        print("🗺️ Amostra do grid de colisão:")
        for i in range(min(8, ROWS)):
            row_str = ""
            for j in range(min(15, COLS)):
                row_str += "█" if self.collision_grid[i][j] == 1 else "·"
            print(f"   Linha {i}: {row_str}")
        print("   (· = livre, ▓ = destrutível, █ = estrutural)")
    
    def get_collision_at(self, grid_x, grid_y):
        from .constants import COLS, ROWS
        
        if (0 <= grid_x < COLS and 0 <= grid_y < ROWS and 
            hasattr(self, 'collision_grid')):
            return self.collision_grid[grid_y][grid_x]
        return 2
    
    def get_tile_type_at(self, grid_x, grid_y):
        collision_value = self.get_collision_at(grid_x, grid_y)
        
        if collision_value == 0:
            return TileType.EMPTY
        elif collision_value == 1:
            return TileType.BRICK
        else:
            return TileType.WALL
    
    def update_animations(self):
        import pygame
        current_time = pygame.time.get_ticks()
        
        directional_characters = [Characters.FINN, Characters.JAKE, Characters.MARCELINE, Characters.PRINCESS_LUMP, Characters.FIRE_PRINCESS, Characters.JELLYBEAN_PRINCESS]
        
        for character in directional_characters:
            if character in self.images and 'walk' in self.images[character]:
                character_data = self.images[character]
                
                if character_data['current_state'] == 'walk':
                    direction = character_data['current_direction']
                    if direction in character_data['walk'] and len(character_data['walk'][direction]) > 0:
                        frame_duration = 1000 // character_data['animation_speed']
                        frame_count = len(character_data['walk'][direction])
                        current_frame_index = (current_time // frame_duration) % frame_count
                        character_data['current_frame'] = current_frame_index

    def get_character_sprite(self, character, is_moving=False, direction=None):
        if character not in self.images or not self.images_loaded[character]:
            return None
            
        directional_characters = [Characters.FINN, Characters.JAKE, Characters.MARCELINE, Characters.PRINCESS_LUMP, Characters.FIRE_PRINCESS, Characters.JELLYBEAN_PRINCESS]
        
        if character in directional_characters and 'idle' in self.images[character]:
            return self._get_directional_sprite(self.images[character], is_moving, direction)
        
        if 'default' in self.images[character]:
            return self.images[character]['default']
            
        return None
    
    def _get_directional_sprite(self, character_data, is_moving, direction):
        if is_moving:
            character_data['current_state'] = 'walk'
            if direction is not None:
                direction_map = {0: 'up', 1: 'right', 2: 'down', 3: 'left'}
                if direction in direction_map:
                    character_data['current_direction'] = direction_map[direction]
        else:
            character_data['current_state'] = 'idle'
        
        current_direction = character_data['current_direction']
        current_state = character_data['current_state']
        
        if current_state == 'idle':
            if current_direction in character_data['idle']:
                return character_data['idle'][current_direction]
            else:
                return character_data['idle'].get('down', None)
        
        elif current_state == 'walk':
            if current_direction in character_data['walk'] and len(character_data['walk'][current_direction]) > 0:
                frame_index = character_data['current_frame']
                frames = character_data['walk'][current_direction]
                return frames[frame_index % len(frames)]
            else:
                if current_direction in character_data['idle']:
                    return character_data['idle'][current_direction]
        
        return None
        

    
    def create_basic_sprites(self):
        bomb_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(bomb_surface, (0, 0, 0), (TILE_SIZE // 2, TILE_SIZE // 2), TILE_SIZE // 2)
        self.images['bomb'] = {'default': bomb_surface}
        self.images_loaded['bomb'] = True

        self.load_explosion_sprite()

    def load_explosion_sprite(self):
        explosion_path = "images/explosion.png"
        
        if os.path.exists(explosion_path):
            try:
                explosion_sprite = pygame.image.load(explosion_path).convert_alpha()
                explosion_sprite = self.scale_sprite_proportional(explosion_sprite, TILE_SIZE)
                
                self.images['explosion'] = {'default': explosion_sprite}
                self.images_loaded['explosion'] = True
                print(f"✅ Sprite de explosão personalizada carregada: {explosion_path}")
                
            except Exception as e:
                print(f"❌ Erro ao carregar explosão personalizada: {e}")
                self.create_explosion_fallback()
        else:
            print(f"⚠️ Sprite de explosão não encontrada: {explosion_path}")
            self.create_explosion_fallback()

    def create_explosion_fallback(self):
        explosion_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(explosion_surface, (255, 165, 0), (0, 0, TILE_SIZE, TILE_SIZE))
        self.images['explosion'] = {'default': explosion_surface}
        self.images_loaded['explosion'] = True
        print("✅ Sprite de explosão fallback criada")

    def get_character_bomb_sprite(self, character):
        if hasattr(self, 'character_bombs') and character in self.character_bombs:
            bomb_sprite = self.character_bombs[character]
            if bomb_sprite is not None:
                return bomb_sprite
        
        if self.is_image_loaded('bomb'):
            return self.images['bomb']['default']
        
        return None

    def draw_character_bomb(self, surface, character, x, y, blinking=False):
        bomb_sprite = self.get_character_bomb_sprite(character)
        
        if bomb_sprite:
            if blinking:
                bomb_sprite.set_alpha(128)
            else:
                bomb_sprite.set_alpha(255)
            
            surface.blit(bomb_sprite, (x, y))
            return True
        
        self.draw_bomb_fallback(surface, x, y, TILE_SIZE, blinking)
        return False

    def is_image_loaded(self, name):
        return self.images_loaded.get(name, False)
    
    def draw_character(self, surface, character, x, y, is_moving=False, direction=None):
        if self.is_image_loaded(character):
            sprite = self.get_character_sprite(character, is_moving, direction)
            if sprite:
                if character == Characters.JAKE:
                    sprite.set_alpha(255)
                
                surface.blit(sprite, (x, y))
                return
        
        self.draw_character_fallback(surface, character, x, y, TILE_SIZE)
    
    def draw_background_map(self, surface):
        if self.images_loaded.get('background_map', False) and self.background_map:
            surface.blit(self.background_map, (0, 0))
            return True
        return False
    
    def draw_sprite(self, surface, sprite_name, x, y, size=TILE_SIZE, **kwargs):
        if sprite_name == "bomb" and 'character' in kwargs:
            character = kwargs['character']
            blinking = kwargs.get('blinking', False)
            if self.draw_character_bomb(surface, character, x, y, blinking):
                return
        
        if self.is_image_loaded(sprite_name):
            if sprite_name in Characters.ALL:
                self.draw_character(surface, sprite_name, x, y, 
                                  kwargs.get('is_moving', False),
                                  kwargs.get('direction', None))
                return
            else:
                sprite = self.images[sprite_name]['default']
                if sprite:
                    if sprite.get_size() != (size, size):
                        sprite = self.scale_sprite_proportional(sprite, size)
                    
                    if kwargs.get("blinking", False):
                        sprite.set_alpha(128)
                    else:
                        sprite.set_alpha(255)
                        
                    surface.blit(sprite, (x, y))
                    return
        
        self.draw_fallback_sprite(surface, sprite_name, x, y, size, **kwargs)
    
    def draw_fallback_sprite(self, surface, sprite_name, x, y, size=TILE_SIZE, **kwargs):
        if sprite_name in Characters.ALL:
            self.draw_character_fallback(surface, sprite_name, x, y, size)
        elif sprite_name == "bomb":
            self.draw_bomb_fallback(surface, x, y, size, kwargs.get("blinking", False))
        elif sprite_name == "explosion":
            self.draw_explosion_fallback(surface, x, y, size)
        elif sprite_name.startswith("powerup"):
            self.draw_powerup_fallback(surface, sprite_name, x, y, size)
        elif sprite_name == "wall":
            self.draw_wall_fallback(surface, x, y, size)
        elif sprite_name == "brick":
            self.draw_brick_fallback(surface, x, y, size)
    
    def draw_character_fallback(self, surface, character, x, y, size):
        colors = {
            Characters.FINN: Colors.BLUE,
            Characters.JAKE: Colors.ORANGE,
            Characters.MARCELINE: Colors.PURPLE,
            Characters.PRINCESS_LUMP: (255, 20, 147)
        }
        
        color = colors.get(character, Colors.YELLOW)
        
        pygame.draw.rect(surface, color, (x + 2, y + 2, size - 4, size - 4))
        pygame.draw.rect(surface, Colors.BLACK, (x + 2, y + 2, size - 4, size - 4), 2)
        
        eye_size = max(2, size // 10)
        pygame.draw.circle(surface, Colors.WHITE, (x + size//4, y + size//3), eye_size)
        pygame.draw.circle(surface, Colors.WHITE, (x + 3*size//4, y + size//3), eye_size)
        pygame.draw.circle(surface, Colors.BLACK, (x + size//4, y + size//3), eye_size//2)
        pygame.draw.circle(surface, Colors.BLACK, (x + 3*size//4, y + size//3), eye_size//2)
        
        mouth_width = size // 4
        mouth_y = y + 2 * size // 3
        pygame.draw.rect(surface, Colors.BLACK, (x + size//2 - mouth_width//2, mouth_y, mouth_width, 2))
        
        if character == Characters.FINN:
            pygame.draw.rect(surface, Colors.WHITE, (x + size//4, y, size//2, size//4))
        elif character == Characters.MARCELINE:
            pygame.draw.rect(surface, Colors.BLACK, (x + size//6, y, 2*size//3, size//3))
    
    def draw_bomb_fallback(self, surface, x, y, size, blinking=False):
        center = (x + size//2, y + size//2)
        radius = size//3
        
        color = Colors.DARK_GRAY if blinking else Colors.BLACK
        
        pygame.draw.circle(surface, color, center, radius)
        pygame.draw.circle(surface, Colors.WHITE, center, radius, 2)
        
        fuse_start = (x + size//2, y + size//6)
        fuse_end = (x + size//2 - size//8, y)
        pygame.draw.line(surface, (139, 69, 19), fuse_start, fuse_end, 3)
        
        if blinking:
            pygame.draw.circle(surface, Colors.YELLOW, fuse_end, 3)
    
    def draw_explosion_fallback(self, surface, x, y, size):
        center_size = size // 2
        center_pos = (x + size//4, y + size//4)
        pygame.draw.rect(surface, Colors.EXPLOSION_CENTER, (*center_pos, center_size, center_size))
        
        flame_size = size // 4
        positions = [
            (x, y + size//4),
            (x + 3*size//4, y + size//4),
            (x + size//4, y),
            (x + size//4, y + 3*size//4)
        ]
        
        for pos in positions:
            pygame.draw.rect(surface, Colors.EXPLOSION_COLOR, (*pos, flame_size, flame_size))
    
    def draw_powerup_fallback(self, surface, powerup_type, x, y, size):
        colors = {
            "powerup_bomb": Colors.POWERUP_BOMB,
            "powerup_range": Colors.POWERUP_RANGE,
            "powerup_speed": Colors.POWERUP_SPEED
        }
        
        letters = {
            "powerup_bomb": "B",
            "powerup_range": "R", 
            "powerup_speed": "S"
        }
        
        color = colors.get(powerup_type, Colors.WHITE)
        letter = letters.get(powerup_type, "?")
        
        pygame.draw.rect(surface, color, (x + 2, y + 2, size - 4, size - 4))
        pygame.draw.rect(surface, Colors.BLACK, (x + 2, y + 2, size - 4, size - 4), 2)
        
        font = pygame.font.Font(None, size//2)
        text = font.render(letter, True, Colors.BLACK)
        text_rect = text.get_rect(center=(x + size//2, y + size//2))
        surface.blit(text, text_rect)
    
    def draw_wall_fallback(self, surface, x, y, size):
        pygame.draw.rect(surface, Colors.WALL_COLOR, (x, y, size, size))
        pygame.draw.rect(surface, Colors.BLACK, (x, y, size, size), 2)
    
    def draw_brick_fallback(self, surface, x, y, size):
        pygame.draw.rect(surface, Colors.BRICK_COLOR, (x, y, size, size))
        pygame.draw.rect(surface, (139, 69, 19), (x, y, size, size), 2)
        
        mid_y = y + size // 2
        pygame.draw.line(surface, (160, 82, 45), (x, mid_y), (x + size, mid_y), 1)