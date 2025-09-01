import pygame
import sys
import random
from .constants import *
from .sprites import SpriteManager
from .audio import AudioManager
from .ui import UI
from .game_map import GameMap
from .entities import Player, Enemy, Bomb, Explosion

class EnemyBombCoordinator:
    def __init__(self):
        self.current_bomber = None
        self.bomb_cooldown_time = 0
        
    def can_enemy_place_bomb(self, enemy, enemies, bombs, game_map):
        if self.current_bomber is not None and self.current_bomber != enemy:
            return False
            
        if pygame.time.get_ticks() < self.bomb_cooldown_time:
            return False
            
        return self.is_safe_to_bomb(enemy, enemies, bombs, game_map)
    
    def register_bomb_placement(self, enemy):
        self.current_bomber = enemy
        self.bomb_cooldown_time = pygame.time.get_ticks() + 3000
        
    def clear_current_bomber(self):
        if self.current_bomber and pygame.time.get_ticks() > self.bomb_cooldown_time:
            self.current_bomber = None
    
    def is_safe_to_bomb(self, enemy, enemies, bombs, game_map):
        grid_x, grid_y = enemy.get_grid_pos()
        
        safe_escape_routes = 0
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            
            for distance in range(1, 5):
                test_x = grid_x + dx * distance
                test_y = grid_y + dy * distance
                
                if not (0 <= test_x < COLS and 0 <= test_y < ROWS):
                    break
                
                if not game_map.is_walkable(test_x, test_y):
                    break
                
                will_be_safe = True
                
                for bomb in bombs:
                    if self.is_position_in_bomb_range(test_x, test_y, bomb):
                        will_be_safe = False
                        break
                
                if (test_x == grid_x and abs(test_y - grid_y) <= enemy.bomb_range) or \
                   (test_y == grid_y and abs(test_x - grid_x) <= enemy.bomb_range):
                    if distance <= 3:
                        will_be_safe = False
                
                if will_be_safe:
                    safe_escape_routes += 1
                    break
        
        return safe_escape_routes >= 2
    
    def is_position_in_bomb_range(self, x, y, bomb):
        if y == bomb.grid_y:
            distance = abs(x - bomb.grid_x)
            if distance <= bomb.explosion_range:
                return True
        
        if x == bomb.grid_x:
            distance = abs(y - bomb.grid_y)
            if distance <= bomb.explosion_range:
                return True
        
        return False

class BombermanGame:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        
    
        self.state = GameState.START
        self.score = 0
        self.level = 1
        self.sprite_manager = SpriteManager()
        self.audio_manager = AudioManager()
        self.ui = UI(screen)
        self.game_map = GameMap(self.sprite_manager)
        
       
        self.selected_character = Characters.FINN
        self.selected_character_index = 0
        
        
        self.player = None
        self.enemies = []
        self.bombs = []
        self.explosions = []
       
        self.keys = {}
        self.key_pressed = {}
        
        self.enemy_bomb_coordinator = EnemyBombCoordinator()
        
        print("🎮 Jogo BOOM na Terra de Ooo inicializado!")
    
    def run(self):
       
        while self.running:
            dt = self.clock.tick(FPS)
            
            self.handle_events()
            self.update(dt)
            self.render()
        
        
        self.audio_manager.cleanup()
    
    def handle_events(self):
       
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self.keys[event.key] = True
                self.key_pressed[event.key] = True
                self.handle_key_press(event.key)
            
            elif event.type == pygame.KEYUP:
                self.keys[event.key] = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event.pos)
    
    def handle_key_press(self, key):
        
        if self.state == GameState.START:
            if key == pygame.K_RETURN:
                self.start_character_select()
                
        elif self.state == GameState.CHARACTER_SELECT:
            if key == pygame.K_LEFT:
                self.selected_character_index = (self.selected_character_index - 1) % len(Characters.ALL)
                self.selected_character = Characters.ALL[self.selected_character_index]
                self.audio_manager.play_menu_sound()
            elif key == pygame.K_RIGHT:
                self.selected_character_index = (self.selected_character_index + 1) % len(Characters.ALL)
                self.selected_character = Characters.ALL[self.selected_character_index]
                self.audio_manager.play_menu_sound()
            elif key == pygame.K_UP:
                self.selected_character_index = (self.selected_character_index - 2) % len(Characters.ALL)
                self.selected_character = Characters.ALL[self.selected_character_index]
                self.audio_manager.play_menu_sound()
            elif key == pygame.K_DOWN:
                self.selected_character_index = (self.selected_character_index + 2) % len(Characters.ALL)
                self.selected_character = Characters.ALL[self.selected_character_index]
                self.audio_manager.play_menu_sound()
            elif key == pygame.K_RETURN:
                self.start_game()
            elif key == pygame.K_ESCAPE:
                self.state = GameState.START
                
        elif self.state == GameState.PLAYING:
            if key == pygame.K_SPACE:
                self.place_bomb()
            elif key == pygame.K_p:
                self.toggle_pause()
            elif key == pygame.K_ESCAPE:
                self.state = GameState.START
                self.audio_manager.stop_background_music()
                
        elif self.state == GameState.PAUSED:
            if key == pygame.K_p:
                self.toggle_pause()
            elif key == pygame.K_ESCAPE:
                self.state = GameState.START
                self.audio_manager.stop_background_music()
                
        elif self.state in [GameState.GAME_OVER, GameState.VICTORY]:
            if key == pygame.K_RETURN:
                if self.state == GameState.VICTORY:
                    self.next_level()
                else:
                    self.restart_game()
            elif key == pygame.K_ESCAPE:
                self.state = GameState.START
        
        
        if key == pygame.K_m:
            self.audio_manager.toggle_mute()
    
    def handle_mouse_click(self, pos):
        
        button_size = 40
        mute_button_x = SCREEN_WIDTH - button_size - 10
        mute_button_y = 10
        mute_button_rect = pygame.Rect(mute_button_x, mute_button_y, button_size, button_size)
        
        if mute_button_rect.collidepoint(pos):
            self.audio_manager.toggle_mute()
            return  
        
        if self.state == GameState.START:
            
            button_width, button_height = 200, 50
            button_x = SCREEN_WIDTH // 2 - button_width // 2
            button_y = SCREEN_HEIGHT // 2
            start_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            if start_button_rect.collidepoint(pos):
                self.audio_manager.play_menu_sound()
                self.start_character_select()
        
        elif self.state == GameState.CHARACTER_SELECT:
            
            character_size = 120
            spacing = 80
            start_x = SCREEN_WIDTH // 2 - character_size - spacing // 2
            start_y = 140
            
            for i, character in enumerate(Characters.ALL):
                row = i // 2
                col = i % 2
                x = start_x + col * (character_size + spacing)
                y = start_y + row * (character_size + spacing)
                
                char_rect = pygame.Rect(x, y, character_size, character_size)
                if char_rect.collidepoint(pos):
                    self.selected_character_index = i
                    self.selected_character = character
                    self.audio_manager.play_menu_sound()
                    break
        
        elif self.state == GameState.GAME_OVER:
            
            button_width, button_height = 180, 40
            restart_button_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - button_width // 2, 
                SCREEN_HEIGHT // 2 + 60, 
                button_width, button_height
            )
            menu_button_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - button_width // 2,
                SCREEN_HEIGHT // 2 + 110, 
                button_width, button_height
            )
            
            if restart_button_rect.collidepoint(pos):
                self.audio_manager.play_menu_sound()
                self.restart_game()
            elif menu_button_rect.collidepoint(pos):
                self.audio_manager.play_menu_sound()
                self.return_to_menu()
        
        elif self.state == GameState.VICTORY:
            
            button_width, button_height = 180, 40
            next_button_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - button_width // 2,
                SCREEN_HEIGHT // 2 + 60, 
                button_width, button_height
            )
            menu_button_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - button_width // 2,
                SCREEN_HEIGHT // 2 + 110, 
                button_width, button_height
                
            )
            
            if next_button_rect.collidepoint(pos):
                self.audio_manager.play_menu_sound()
                self.next_level()
            elif menu_button_rect.collidepoint(pos):
                self.audio_manager.play_menu_sound()
                self.return_to_menu()
    
    def update(self, dt):
        
        self.ui.update(dt)
        
        
        self.key_pressed = {}
        
        if self.state == GameState.PLAYING:
            self.update_game(dt)
        elif self.state == GameState.CHARACTER_SELECT:
            
            for enemy in self.enemies:
                enemy.update(dt, self.game_map, self.player, self.bombs, self.enemy_bomb_coordinator)
    
    def update_game(self, dt):
        
        self.sprite_manager.update_animations()
        
        
        self.update_player(dt)
        
        
        self.enemy_bomb_coordinator.clear_current_bomber()
        
        for enemy in self.enemies[:]:  
            if enemy.alive:
                enemy.update(dt, self.game_map, self.player, self.bombs, self.enemy_bomb_coordinator)
        
        
        self.update_bombs(dt)
        
        
        self.update_explosions(dt)
        
        
        if self.game_map.update_powerups(dt, self.player):
            self.score += 50
            self.audio_manager.play_powerup_sound()
        
        
        self.check_collisions()
        
        
        self.check_win_lose_conditions()
    
    def update_player(self, dt):
        
        if not self.player:
            return
        
        self.player.update(dt)
        
        
        dx, dy = 0, 0
        if self.keys.get(pygame.K_a) or self.keys.get(pygame.K_LEFT):
            dx = -1
        if self.keys.get(pygame.K_d) or self.keys.get(pygame.K_RIGHT):
            dx = 1
        if self.keys.get(pygame.K_w) or self.keys.get(pygame.K_UP):
            dy = -1
        if self.keys.get(pygame.K_s) or self.keys.get(pygame.K_DOWN):
            dy = 1
            
        
        if dx != 0 or dy != 0:
            self.player.move(dx, dy, self.game_map, self.bombs)
    
    def update_bombs(self, dt):
       
        for bomb in self.bombs[:]:  
            should_explode = bomb.update(dt, self.game_map, self.player)
            
            if should_explode:
                
                explosion = bomb.explode(self.game_map)
                self.explosions.append(explosion)
                self.bombs.remove(bomb)
                print(f"💥 Bomba explodiu! Bombas restantes: {len([b for b in self.bombs if b.owner == self.player.character])}/{self.player.max_bombs}")
                self.audio_manager.play_explosion_sound()
    
    def update_explosions(self, dt):
        
        for explosion in self.explosions[:]: 
            explosion_ended = explosion.update(dt, self.game_map)
            if explosion_ended:
                self.explosions.remove(explosion)
    
    def check_collisions(self):
        
        if not self.player:
            return
        
        player_rect = self.player.get_rect()
        
        
        for explosion in self.explosions:
           
            bomb_pixel_x = explosion.bomb_x * TILE_SIZE
            bomb_pixel_y = explosion.bomb_y * TILE_SIZE
            
            if self.game_map.can_explosion_reach_player(bomb_pixel_x, bomb_pixel_y, self.player.x, self.player.y):
                
                player_grid_x = int(self.player.x // TILE_SIZE)
                player_grid_y = int(self.player.y // TILE_SIZE)
                
                for tile_x, tile_y in explosion.tiles:
                    if tile_x == player_grid_x and tile_y == player_grid_y:
                        self.player_hit()
                        return
        
        
        for enemy in self.enemies:
            if enemy.alive and player_rect.colliderect(enemy.get_rect()):
                
                if self.game_map.has_clear_line_of_sight(self.player.x, self.player.y, enemy.x, enemy.y):
                    self.player_hit()
                    return
        
       
        for enemy in self.enemies[:]:
            if not enemy.alive:
                continue
            
            for explosion in self.explosions:
               
                bomb_pixel_x = explosion.bomb_x * TILE_SIZE
                bomb_pixel_y = explosion.bomb_y * TILE_SIZE
                
                if self.game_map.can_explosion_reach_player(bomb_pixel_x, bomb_pixel_y, enemy.x, enemy.y):
                  
                    enemy_grid_x = int(enemy.x // TILE_SIZE)
                    enemy_grid_y = int(enemy.y // TILE_SIZE)
                    
                    for tile_x, tile_y in explosion.tiles:
                        if tile_x == enemy_grid_x and tile_y == enemy_grid_y:
                            enemy.alive = False
                            self.score += 100
                            break
    
    def check_win_lose_conditions(self):
        
        if not self.player:
            return
        
        
        if self.player.lives <= 0:
            self.game_over()
        
        
        alive_enemies = [enemy for enemy in self.enemies if enemy.alive]
        if len(alive_enemies) == 0:
            self.victory()
    
    def place_bomb(self):
        
        if not self.player:
            return
        
        
        player_bombs = [bomb for bomb in self.bombs if bomb.owner == self.player.character]
        if len(player_bombs) >= self.player.max_bombs:
            print(f"🚫 Limite de bombas atingido! ({len(player_bombs)}/{self.player.max_bombs})")
            return
        
        
        grid_x, grid_y = self.player.get_grid_pos()
        
        
        for bomb in self.bombs:
            if bomb.grid_x == grid_x and bomb.grid_y == grid_y:
                return
        
        
        new_bomb = Bomb(grid_x, grid_y, self.player.bomb_range, self.player.character)
        self.bombs.append(new_bomb)
        print(f"💣 Bomba criada! Total: {len([b for b in self.bombs if b.owner == self.player.character])}/{self.player.max_bombs}")
        
        
        self.audio_manager.play_bomb_sound()
    
    def player_hit(self):
        
        if not self.player:
            return
        
        self.player.lives -= 1
        
        if self.player.lives > 0:
            
            self.player.x = 1 * TILE_SIZE  
            self.player.y = 2 * TILE_SIZE  
        else:
            self.game_over()
    
    def start_character_select(self):
        
        self.state = GameState.CHARACTER_SELECT
        
        
        self.game_map.generate_level(1)
        
        
        self.player = Player(1, 2, self.selected_character)
        
        
        self.enemies = []
        enemy_characters = [char for char in Characters.ALL if char != self.selected_character]
        positions = self.game_map.get_valid_spawn_positions()
        
        for i, character in enumerate(enemy_characters[:3]):
            if positions:
                pos = random.choice(positions)
                positions.remove(pos)
                enemy = Enemy(pos[0], pos[1], character)
                self.enemies.append(enemy)
        
        self.audio_manager.play_menu_sound()
    
    def start_game(self):
       
        self.state = GameState.PLAYING
        
       
        if self.level == 1:
            self.score = 0
        
   
        self.game_map.generate_level(self.level)
 
        self.player = Player(1, 2, self.selected_character)
        
      
        self.create_enemies()
        
    
        self.bombs = []
        self.explosions = []
      
        self.audio_manager.start_background_music()
        
        print(f"🎮 Jogo iniciado - Nível {self.level}")
    
    def create_enemies(self):
        
        self.enemies = []
        
       
        enemy_characters = [char for char in Characters.ALL if char != self.selected_character]
        
      
        corner_positions = [
            (COLS - 2, 1),       
            (1, ROWS - 2),        
            (COLS - 2, ROWS - 2), 
        ]
        
        corner_names = ["superior direito", "inferior esquerdo", "inferior direito"]
        
        print(f"🎯 Criando inimigos nas posições garantidas dos cantos:")
        
       
        for i, character in enumerate(enemy_characters[:3]): 
            if i < len(corner_positions):
                pos = corner_positions[i]
                x, y = pos
                
               
                if (0 <= x < COLS and 0 <= y < ROWS and 
                    self.game_map.is_walkable(x, y)):
                    
                    enemy = Enemy(x, y, character)
                    self.enemies.append(enemy)
                    corner_name = corner_names[i]
                    print(f"🤖 Inimigo {character} criado no canto {corner_name}: ({x}, {y}) ✅")
                else:
                    print(f"❌ ERRO: Posição ({x}, {y}) ainda não é walkable - verificar geração do mapa")
            else:
                print(f"⚠️ Limite de posições atingido - {character} não foi criado")
        
        print(f"🎯 Total de inimigos criados: {len(self.enemies)}")
        
        if len(self.enemies) == 0:
            pass
        elif len(self.enemies) < 3:
            pass
    
    def restart_game(self):
       
        self.level = 1
        self.score = 0
        self.start_game()
    
    def next_level(self):
      
        self.level += 1
        self.score += 500 * self.level 
        self.start_game()
    
    def game_over(self):
        
        self.state = GameState.GAME_OVER
        self.audio_manager.stop_background_music()
        self.audio_manager.play_game_over_sound()
        print(f"💀 Game Over - Pontuação: {self.score}, Nível: {self.level}")
    
    def victory(self):
        
        self.state = GameState.VICTORY
        self.score += 500 * self.level
        self.audio_manager.play_victory_sound()
        print(f"🏆 Vitória - Nível {self.level} completo!")
    
    def toggle_pause(self):
       
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED
            self.audio_manager.stop_background_music()
        elif self.state == GameState.PAUSED:
            self.state = GameState.PLAYING
            self.audio_manager.start_background_music()
    
    def return_to_menu(self):
        self.state = GameState.START
        self.audio_manager.stop_background_music()
        
    def next_level(self):
        self.level += 1
        self.start_game()
    
    def render(self):
      
        self.screen.fill(Colors.BLACK)
        
        if self.state == GameState.START:
            self.ui.draw_start_screen()
            
        elif self.state == GameState.CHARACTER_SELECT:
            self.ui.draw_character_select_screen(
                self.selected_character, self.selected_character_index, self.sprite_manager
            )
            
        elif self.state in [GameState.PLAYING, GameState.PAUSED]:
            self.render_game()
            
        elif self.state == GameState.GAME_OVER:
            self.ui.draw_game_over_screen(self.score, self.level)
            
        elif self.state == GameState.VICTORY:
            self.ui.draw_victory_screen(self.score)
        
    
        mute_button = self.ui.draw_mute_button(self.audio_manager.is_muted)
        
        pygame.display.flip()
    
    def render_game(self):
       
        if not self.sprite_manager.draw_background_map(self.screen):
            
            self.screen.fill((34, 139, 34))
        
        
        self.game_map.render(self.screen, self.sprite_manager)
        
       
        for bomb in self.bombs:
            self.sprite_manager.draw_sprite(
                self.screen, "bomb", bomb.x, bomb.y, TILE_SIZE, 
                blinking=bomb.blinking,
                character=bomb.owner  
            )
        
      
        if self.player:
            self.sprite_manager.draw_character(
                self.screen, self.player.character, self.player.x, self.player.y,
                is_moving=self.player.is_moving,
                direction=self.player.direction
            )
        
       
        for enemy in self.enemies:
            if enemy.alive:
                enemy_direction = getattr(enemy, 'direction', None)
                self.sprite_manager.draw_character(
                    self.screen, enemy.character, enemy.x, enemy.y,
                    is_moving=enemy.is_moving if hasattr(enemy, 'is_moving') else False,
                    direction=enemy_direction
                )
        
        
        bombs_count = self.player.max_bombs if self.player else 0
        self.ui.draw_game_screen(self.score, self.player.lives if self.player else 0, self.level, bombs_count)
        
       
        if self.state == GameState.PAUSED:
            self.ui.draw_pause_overlay()


