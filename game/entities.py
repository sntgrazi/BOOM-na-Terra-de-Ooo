import pygame
import math
import random
from .constants import *

class Player:
    def __init__(self, x, y, character=Characters.FINN):
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.character = character
        self.speed = PLAYER_SPEED
        self.max_bombs = 1
        self.bomb_range = 2
        self.lives = 3
        self.is_moving = False
        self.direction = Direction.DOWN
    
    def update(self, dt):
        pass
    
    def move(self, dx, dy, game_map, bombs=None):
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        if game_map.can_player_move_to(new_x, new_y):
            self.x = new_x
            self.y = new_y
            self.is_moving = True
            
            if dx > 0:
                self.direction = Direction.RIGHT
            elif dx < 0:
                self.direction = Direction.LEFT
            elif dy > 0:
                self.direction = Direction.DOWN
            elif dy < 0:
                self.direction = Direction.UP
        else:
            self.is_moving = False
    
    def get_grid_pos(self):
        return (
            int((self.x + TILE_SIZE // 2) // TILE_SIZE),
            int((self.y + TILE_SIZE // 2) // TILE_SIZE)
        )
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, TILE_SIZE, TILE_SIZE)

class Enemy:
    def __init__(self, x, y, character=Characters.JAKE):
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.character = character
        self.speed = ENEMY_SPEED
        self.direction = random.randint(0, 3)
        self.last_direction_change = 0
        self.alive = True
        self.is_moving = False
        
        self.max_bombs = 1
        self.bomb_range = 2
        self.last_bomb_time = 0
        self.bomb_cooldown = random.randint(2000, 3000)
        self.spawn_time = pygame.time.get_ticks()
        self.mode = "explore"
        self.last_direction_change = pygame.time.get_ticks()
        
        self.escape_direction = None
        self.escape_mode_until = 0
        
        print(f"🤖 Inimigo {character} criado com cooldown inicial de {self.bomb_cooldown}ms")
        
    def update(self, dt, game_map, player, bombs, bomb_coordinator=None):
        if not self.alive:
            return
        
        current_time = pygame.time.get_ticks()
        
        self.check_powerup_collection(game_map)
        
        self.update_ai_mode(player, bombs, current_time)
        
        time_since_last_bomb = current_time - self.last_bomb_time
        time_since_spawn = current_time - self.spawn_time
        
        if time_since_last_bomb > self.bomb_cooldown and time_since_spawn > 2000:
            my_bombs = sum(1 for bomb in bombs if bomb.owner == self.character)
            
            if my_bombs == 0:
                grid_x, grid_y = self.get_grid_pos()
                player_grid_x, player_grid_y = player.get_grid_pos()
                distance_to_player = abs(grid_x - player_grid_x) + abs(grid_y - player_grid_y)
                
                destructible_blocks = self.count_destructible_blocks_in_range(game_map, grid_x, grid_y)
                player_nearby = distance_to_player <= 5
                random_placement = random.random() < 0.4
                
                should_place_bomb = False
                reason = ""
                
                if destructible_blocks > 0:
                    should_place_bomb = True
                    reason = f"quebrar {destructible_blocks} bloco(s) destrutível(is)"
                elif player_nearby:
                    should_place_bomb = True
                    reason = f"atacar jogador (distância: {distance_to_player})"
                elif random_placement:
                    should_place_bomb = True
                    reason = "exploração aleatória"
                
                if should_place_bomb:
                    if bomb_coordinator and bomb_coordinator.can_enemy_place_bomb(self, [], bombs, game_map):
                        safe_escape_routes = self.analyze_safe_escape_routes(game_map, bombs, grid_x, grid_y)
                        
                        if len(safe_escape_routes) >= 1:
                            if self.place_bomb(game_map, bombs, current_time):
                                bomb_coordinator.register_bomb_placement(self)
                                best_route = safe_escape_routes[0]
                                self.escape_direction = best_route['direction']
                                self.escape_mode_until = current_time + 4000
                                print(f"💣✅ {self.character} colocou bomba coordenada para {reason}")
                            
                            self.bomb_cooldown = random.randint(3000, 5000)
                        else:
                            print(f"💣❌ {self.character} cancelou - sem rotas seguras")
                            self.bomb_cooldown = random.randint(1000, 2000)
                    else:
                        if bomb_coordinator:
                            print(f"💣⏳ {self.character} aguardando vez para colocar bomba")
                        self.bomb_cooldown = random.randint(500, 1500)
        
        self.update_movement(game_map, bombs, player, current_time)
    
    def analyze_safe_escape_routes(self, game_map, bombs, grid_x, grid_y):
        safe_routes = []
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            
            for distance in range(1, 5):
                test_x = grid_x + dx * distance
                test_y = grid_y + dy * distance
                
                if not (0 <= test_x < COLS and 0 <= test_y < ROWS):
                    break
                
                if not game_map.is_walkable(test_x, test_y):
                    break
                
                is_safe = True
                
                for bomb in bombs:
                    if self.is_position_dangerous(test_x, test_y, bomb):
                        is_safe = False
                        break
                
                if (test_x == grid_x and abs(test_y - grid_y) <= self.bomb_range) or \
                   (test_y == grid_y and abs(test_x - grid_x) <= self.bomb_range):
                    if distance <= 3:
                        is_safe = False
                
                if is_safe:
                    safe_routes.append({
                        'direction': direction,
                        'position': (test_x, test_y),
                        'distance': distance
                    })
                    break
        
        return safe_routes
    
    def is_position_dangerous(self, x, y, bomb):
        if y == bomb.grid_y:
            distance = abs(x - bomb.grid_x)
            if distance <= bomb.explosion_range:
                return True
        
        if x == bomb.grid_x:
            distance = abs(y - bomb.grid_y)
            if distance <= bomb.explosion_range:
                return True
        
        return False
    
    def check_powerup_collection(self, game_map):
        grid_x, grid_y = self.get_grid_pos()
        powerup = game_map.get_powerup(grid_x, grid_y)
        
        if powerup and powerup.apply_to_enemy(self):
            game_map.remove_powerup(grid_x, grid_y)
    
    def update_ai_mode(self, player, bombs, current_time):
        if random.random() < 0.01:
            distance_to_player = math.sqrt(
                (player.x - self.x)**2 + (player.y - self.y)**2
            ) / TILE_SIZE
            
            if distance_to_player <= 5:
                self.mode = "attack"
            else:
                self.mode = "explore"
    
    def assess_danger_level(self, bombs, current_time):
        grid_x, grid_y = self.get_grid_pos()
        max_danger = 0
        
        for bomb in bombs:
            danger = 0
            
            if self.is_position_in_bomb_range(grid_x, grid_y, bomb):
                time_left = BOMB_TIMER - (pygame.time.get_ticks() - bomb.timer)
                manhattan_distance = abs(bomb.grid_x - grid_x) + abs(bomb.grid_y - grid_y)
                
                if time_left < 1000:
                    danger = 3
                elif time_left < 2000:
                    danger = 2
                elif manhattan_distance <= 1:
                    danger = 2
                else:
                    danger = 1
                
                if bomb.owner == self.character and hasattr(self, 'post_bomb_grace_time'):
                    if current_time < self.post_bomb_grace_time:
                        danger = max(0, danger - 1)
            
            else:
                manhattan_distance = abs(bomb.grid_x - grid_x) + abs(bomb.grid_y - grid_y)
                if manhattan_distance <= 2 and bomb.owner != self.character:
                    danger = 1
            
            max_danger = max(max_danger, danger)
        
        return max_danger
    
    def calculate_distance_to_player(self, player):
        distance_pixels = math.sqrt(
            (player.x - self.x)**2 + (player.y - self.y)**2
        )
        return distance_pixels / TILE_SIZE

    def is_in_immediate_bomb_danger(self, bombs):
        grid_x, grid_y = self.get_grid_pos()
        
        for bomb in bombs:
            if ((grid_x == bomb.grid_x and abs(grid_y - bomb.grid_y) <= bomb.explosion_range) or
                (grid_y == bomb.grid_y and abs(grid_x - bomb.grid_x) <= bomb.explosion_range)):
                
                return True
        return False

    def is_in_bomb_explosion_path(self, x, y, bomb):
        if x != bomb.grid_x and y != bomb.grid_y:
            return False
        
        if x == bomb.grid_x:
            distance = abs(y - bomb.grid_y)
            if distance > bomb.explosion_range:
                return False
            
            min_y = min(y, bomb.grid_y)
            max_y = max(y, bomb.grid_y)
            
            current_y = bomb.grid_y
            step = 1 if y > bomb.grid_y else -1
            
            while current_y != y:
                current_y += step
                if hasattr(self, '_temp_game_map'):
                    if not self._temp_game_map.is_walkable(x, current_y):
                        return False
                        
        elif y == bomb.grid_y:
            distance = abs(x - bomb.grid_x)
            if distance > bomb.explosion_range:
                return False
                
            current_x = bomb.grid_x
            step = 1 if x > bomb.grid_x else -1
            
            while current_x != x:
                current_x += step
                if hasattr(self, '_temp_game_map'):
                    if not self._temp_game_map.is_walkable(current_x, y):
                        return False
        
        return True

    def should_place_bomb(self, game_map, player, bombs):
        my_bombs = sum(1 for bomb in bombs if bomb.owner == self.character)
        total_bombs = len(bombs)
        
        if my_bombs >= self.max_bombs or total_bombs >= 5:
            return False
        
        grid_x, grid_y = self.get_grid_pos()
        
        escape_routes = self.count_escape_routes(game_map, bombs, grid_x, grid_y)
        if escape_routes < 2:
            return False
        
        if not self.can_escape_own_bomb(game_map, bombs, grid_x, grid_y):
            return False
        
        for bomb in bombs:
            if bomb.owner != self.character:
                if abs(bomb.grid_x - grid_x) + abs(bomb.grid_y - grid_y) <= 4:
                    return False
        
        distance_to_player = math.sqrt(
            (player.x - self.x)**2 + (player.y - self.y)**2
        )
        tile_distance = distance_to_player / TILE_SIZE
        
        if 3 <= tile_distance <= 5:
            player_grid_x, player_grid_y = player.get_grid_pos()
            
            if self.will_bomb_hit_player(grid_x, grid_y, player_grid_x, player_grid_y):
                return random.random() < self.aggression_level
        
        strategic_bricks = self.count_strategic_bricks(game_map, grid_x, grid_y)
        if strategic_bricks >= 2:
            return random.random() < 0.4
        
        return random.random() < 0.1
    
    def should_place_bomb_aggressive(self, game_map, player, bombs):
        my_bombs = sum(1 for bomb in bombs if bomb.owner == self.character)
        if my_bombs >= self.max_bombs:
            return False
        
        if self.panic_mode:
            return False
        
        grid_x, grid_y = self.get_grid_pos()
        player_grid_x, player_grid_y = player.get_grid_pos()
        
        distance_to_player = abs(grid_x - player_grid_x) + abs(grid_y - player_grid_y)
        
        if 2 <= distance_to_player <= 4:
            if self.will_bomb_hit_player(grid_x, grid_y, player_grid_x, player_grid_y):
                if self.count_escape_routes(game_map, bombs, grid_x, grid_y) >= 1:
                    return random.random() < self.aggression_level * 1.5
        
        strategic_bricks = self.count_strategic_bricks(game_map, grid_x, grid_y)
        if strategic_bricks >= 1:
            if distance_to_player <= 5:
                if self.count_escape_routes(game_map, bombs, grid_x, grid_y) >= 1:
                    return random.random() < self.aggression_level
        
        if distance_to_player <= 3:
            if self.count_escape_routes(game_map, bombs, grid_x, grid_y) >= 2:
                return random.random() < (self.aggression_level * 0.5)
        
        return False

    def can_safely_escape_from_bomb(self, game_map, bombs, bomb_grid_x, bomb_grid_y):
        grid_x, grid_y = self.get_grid_pos()
        
        immediate_exits = 0
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            check_x = grid_x + dx
            check_y = grid_y + dy
            
            if (0 <= check_x < COLS and 0 <= check_y < ROWS and 
                game_map.is_walkable(check_x, check_y)):
                immediate_exits += 1
        
        if immediate_exits == 0:
            return False
        
        simulated_bomb = type('obj', (object,), {
            'grid_x': bomb_grid_x,
            'grid_y': bomb_grid_y,
            'owner': self.character,
            'explosion_range': 2
        })
        
        test_bombs = list(bombs) + [simulated_bomb]
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            
            for distance in range(1, 4):
                check_x = grid_x + dx * distance
                check_y = grid_y + dy * distance
                
                if not (0 <= check_x < COLS and 0 <= check_y < ROWS):
                    break
                
                if not game_map.is_walkable(check_x, check_y):
                    break
                
                safe_from_simulated_bomb = not self.is_in_bomb_explosion_path(check_x, check_y, simulated_bomb)
                
                if safe_from_simulated_bomb:
                    return True
        
        return immediate_exits >= 2

    def should_place_bomb_smart(self, game_map, player, bombs):
        my_bombs = sum(1 for bomb in bombs if bomb.owner == self.character)
        if my_bombs >= self.max_bombs:
            return False
        
        if self.panic_mode:
            return False
        
        grid_x, grid_y = self.get_grid_pos()
        player_grid_x, player_grid_y = player.get_grid_pos()
        
        distance_to_player = abs(grid_x - player_grid_x) + abs(grid_y - player_grid_y)
        
        if 2 <= distance_to_player <= 5:
            if self.will_bomb_hit_player(grid_x, grid_y, player_grid_x, player_grid_y):
                escape_routes = self.calculate_escape_routes(game_map, bombs, grid_x, grid_y)
                if len(escape_routes) >= 2:
                    print(f"🎯 {self.character} vai atacar o jogador! Distância: {distance_to_player}")
                    return random.random() < 0.7
        
        destructible_info = self.find_best_destructible_target(game_map)
        if destructible_info:
            escape_routes = self.calculate_escape_routes(game_map, bombs, grid_x, grid_y)
            if len(escape_routes) >= 1:
                print(f"💎 {self.character} vai quebrar bloco destrutível!")
                return random.random() < 0.5
        
        if distance_to_player >= 4:
            if self.is_tactical_position(game_map, player, grid_x, grid_y):
                escape_routes = self.calculate_escape_routes(game_map, bombs, grid_x, grid_y)
                if len(escape_routes) >= 2:
                    print(f"🛡️ {self.character} posicionamento tático!")
                    return random.random() < 0.3
        
        return False
    
    def calculate_escape_routes(self, game_map, bombs, bomb_x, bomb_y):
        escape_routes = []
        
        future_bombs = list(bombs)
        simulated_bomb = type('obj', (object,), {
            'grid_x': bomb_x,
            'grid_y': bomb_y,
            'explosion_range': self.bomb_range,
            'owner': self.character
        })()
        future_bombs.append(simulated_bomb)
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            
            for distance in range(1, 4):
                escape_x = bomb_x + dx * distance
                escape_y = bomb_y + dy * distance
                
                if not (0 <= escape_x < COLS and 0 <= escape_y < ROWS):
                    break
                
                if not game_map.is_walkable(escape_x, escape_y):
                    break
                
                is_safe = True
                for bomb in future_bombs:
                    if self.is_position_in_bomb_range(escape_x, escape_y, bomb):
                        is_safe = False
                        break
                
                if is_safe:
                    escape_routes.append({
                        'direction': direction,
                        'distance': distance,
                        'position': (escape_x, escape_y)
                    })
                    break
        
        return escape_routes
    
    def find_best_destructible_target(self, game_map):
        grid_x, grid_y = self.get_grid_pos()
        best_target = None
        max_value = 0
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            for distance in range(1, self.bomb_range + 1):
                target_x = grid_x + dx * distance
                target_y = grid_y + dy * distance
                
                if not (0 <= target_x < COLS and 0 <= target_y < ROWS):
                    break
                
                tile_type = game_map.get_tile(target_x, target_y)
                
                if tile_type == TileType.WALL:
                    break
                
                if tile_type == TileType.BRICK:
                    value = self.calculate_destructible_value(game_map, target_x, target_y)
                    if value > max_value:
                        max_value = value
                        best_target = {
                            'position': (target_x, target_y),
                            'value': value,
                            'direction': direction
                        }
                    break
        
        return best_target
    
    def calculate_destructible_value(self, game_map, block_x, block_y):
        value = 1
        
        distance_to_edge = min(block_x, block_y, COLS - 1 - block_x, ROWS - 1 - block_y)
        if distance_to_edge <= 2:
            value += 2
        
        adjacent_blocks = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                check_x, check_y = block_x + dx, block_y + dy
                if (0 <= check_x < COLS and 0 <= check_y < ROWS and
                    game_map.get_tile(check_x, check_y) == TileType.BRICK):
                    adjacent_blocks += 1
        
        value += adjacent_blocks * 0.5
        
        return value
    
    def is_tactical_position(self, game_map, player, grid_x, grid_y):
        player_grid_x, player_grid_y = player.get_grid_pos()
        
        if self.is_in_player_path(game_map, player, grid_x, grid_y):
            return True
        
        center_x, center_y = COLS // 2, ROWS // 2
        distance_to_center = abs(grid_x - center_x) + abs(grid_y - center_y)
        if distance_to_center <= 3:
            return True
        
        return False
    
    def is_in_player_path(self, game_map, player, grid_x, grid_y):
        player_grid_x, player_grid_y = player.get_grid_pos()
        
        if grid_x == player_grid_x or grid_y == player_grid_y:
            return True
        
        walkable_neighbors = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                check_x, check_y = grid_x + dx, grid_y + dy
                if (0 <= check_x < COLS and 0 <= check_y < ROWS and
                    game_map.is_walkable(check_x, check_y)):
                    walkable_neighbors += 1
        
        return walkable_neighbors <= 3
    
    def should_place_bomb_simple(self, game_map, player, bombs):
        my_bombs = sum(1 for bomb in bombs if bomb.owner == self.character)
        if my_bombs >= self.max_bombs:
            return False
        
        grid_x, grid_y = self.get_grid_pos()
        player_grid_x, player_grid_y = player.get_grid_pos()
        
        if grid_x <= 1 or grid_y <= 1 or grid_x >= COLS-2 or grid_y >= ROWS-2:
            return False
        
        escape_directions = 0
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            test_x, test_y = grid_x + dx, grid_y + dy
            
            if (0 <= test_x < COLS and 0 <= test_y < ROWS and 
                game_map.is_walkable(test_x, test_y)):
                safe_from_bombs = True
                for bomb in bombs:
                    if self.is_position_in_bomb_range(test_x, test_y, bomb):
                        safe_from_bombs = False
                        break
                if safe_from_bombs:
                    escape_directions += 1
        
        if escape_directions < 2:
            return False
        
        distance_to_player = abs(grid_x - player_grid_x) + abs(grid_y - player_grid_y)
        
        if 2 <= distance_to_player <= 4:
            if (grid_x == player_grid_x or grid_y == player_grid_y):
                return random.random() < 0.6
        
        destructible_nearby = False
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            for i in range(1, self.bomb_range + 1):
                check_x = grid_x + dx * i
                check_y = grid_y + dy * i
                
                if not (0 <= check_x < COLS and 0 <= check_y < ROWS):
                    break
                
                tile_type = game_map.get_tile(check_x, check_y)
                if tile_type == TileType.WALL:
                    break
                elif tile_type == TileType.BRICK:
                    destructible_nearby = True
                    break
        
        if destructible_nearby:
            return random.random() < 0.4
        
        if distance_to_player >= 5:
            return random.random() < 0.1
        
        return False

    def can_safely_escape_own_bomb(self, game_map, bombs, grid_x, grid_y):
        explosion_range = self.bomb_range
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            
            safe_distance = 0
            for i in range(1, explosion_range + 3):
                check_x = grid_x + dx * i
                check_y = grid_y + dy * i
                
                if not (0 <= check_x < COLS and 0 <= check_y < ROWS):
                    break
                if not game_map.is_walkable(check_x, check_y):
                    break
                
                safe_distance += 1
            
            if safe_distance >= 3:
                return True
        
        return False

    def has_long_escape_route(self, game_map, bombs, grid_x, grid_y):
        long_routes = 0
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            route_length = 0
            
            for i in range(1, 6):
                check_x = grid_x + dx * i
                check_y = grid_y + dy * i
                
                if not (0 <= check_x < COLS and 0 <= check_y < ROWS):
                    break
                if not game_map.is_walkable(check_x, check_y):
                    break
                
                safe_from_bombs = True
                for bomb in bombs:
                    if abs(bomb.grid_x - check_x) + abs(bomb.grid_y - check_y) <= bomb.explosion_range + 1:
                        safe_from_bombs = False
                        break
                
                if not safe_from_bombs:
                    break
                
                route_length += 1
            
            if route_length >= 3:
                long_routes += 1
        
        return long_routes >= 1

    def should_place_bomb_ultra_safe(self, game_map, player, bombs):
        if len(bombs) > 0:
            return False
        
        if self.panic_mode:
            return False
        
        my_bombs = sum(1 for bomb in bombs if bomb.owner == self.character)
        if my_bombs >= self.max_bombs:
            return False
        
        grid_x, grid_y = self.get_grid_pos()
        
        safe_routes = 0
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            
            route_completely_safe = True
            for distance in range(1, 9):
                check_x = grid_x + dx * distance
                check_y = grid_y + dy * distance
                
                if not (0 <= check_x < COLS and 0 <= check_y < ROWS):
                    break
                if not game_map.is_walkable(check_x, check_y):
                    route_completely_safe = False
                    break
                    
                distance_to_player = abs(check_x - player.get_grid_pos()[0]) + abs(check_y - player.get_grid_pos()[1])
                if distance_to_player <= 2:
                    route_completely_safe = False
                    break
            
            if route_completely_safe and distance >= 6:
                safe_routes += 1
        
        if safe_routes < 3:
            return False
        
        distance_to_player = math.sqrt(
            (player.x - self.x)**2 + (player.y - self.y)**2
        )
        tile_distance = distance_to_player / TILE_SIZE
        
        if tile_distance < 8:
            return False
        
        return random.random() < 0.01
    
    def count_escape_routes(self, game_map, bombs, grid_x, grid_y):
        escape_routes = 0
        
        future_bombs = bombs + [type('', (), {
            'grid_x': grid_x, 
            'grid_y': grid_y, 
            'explosion_range': self.bomb_range,
            'owner': self.character
        })()]
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            
            escape_possible = False
            for escape_distance in range(1, 4):
                escape_x = grid_x + dx * escape_distance
                escape_y = grid_y + dy * escape_distance
                
                if not (0 <= escape_x < COLS and 0 <= escape_y < ROWS):
                    break
                
                if not game_map.is_walkable(escape_x, escape_y):
                    break
                
                position_safe = True
                for bomb in future_bombs:
                    if ((bomb.grid_x == escape_x and abs(bomb.grid_y - escape_y) <= bomb.explosion_range) or
                        (bomb.grid_y == escape_y and abs(bomb.grid_x - escape_x) <= bomb.explosion_range)):
                        position_safe = False
                        break
                
                if position_safe:
                    escape_possible = True
                    break
            
            if escape_possible:
                escape_routes += 1
                
        return escape_routes

    def can_escape_own_bomb(self, game_map, bombs, grid_x, grid_y):
        max_escape_tiles = 4
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            
            for distance in range(1, max_escape_tiles + 1):
                escape_x = grid_x + dx * distance
                escape_y = grid_y + dy * distance
                
                if not (0 <= escape_x < COLS and 0 <= escape_y < ROWS):
                    break
                
                path_clear = True
                for step in range(1, distance + 1):
                    check_x = grid_x + dx * step
                    check_y = grid_y + dy * step
                    if not game_map.is_walkable(check_x, check_y):
                        path_clear = False
                        break
                
                if not path_clear:
                    break
                
                if not ((grid_x == escape_x and abs(grid_y - escape_y) <= self.bomb_range) or
                        (grid_y == escape_y and abs(grid_x - escape_x) <= self.bomb_range)):
                    safe_from_others = True
                    for bomb in bombs:
                        if ((bomb.grid_x == escape_x and abs(bomb.grid_y - escape_y) <= bomb.explosion_range) or
                            (bomb.grid_y == escape_y and abs(bomb.grid_x - escape_x) <= bomb.explosion_range)):
                            safe_from_others = False
                            break
                    
                    if safe_from_others:
                        return True
        
        return False
    
    def has_any_escape_route(self, game_map, bombs, grid_x, grid_y):
        max_escape_distance = 3
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            
            for distance in range(1, max_escape_distance + 1):
                escape_x = grid_x + dx * distance
                escape_y = grid_y + dy * distance
                
                if not (0 <= escape_x < COLS and 0 <= escape_y < ROWS):
                    break
                
                if not game_map.is_walkable(escape_x, escape_y):
                    break
                
                bomb_danger = False
                for bomb in bombs:
                    bomb_distance = abs(escape_x - bomb.grid_x) + abs(escape_y - bomb.grid_y)
                    if bomb_distance <= bomb.explosion_range:
                        bomb_danger = True
                        break
                
                if not bomb_danger:
                    path_clear = True
                    for step in range(1, distance):
                        path_x = grid_x + dx * step
                        path_y = grid_y + dy * step
                        if not game_map.is_walkable(path_x, path_y):
                            path_clear = False
                            break
                    
                    if path_clear:
                        return True
        
        return False
    
    def is_direction_walkable(self, game_map, grid_x, grid_y, dx, dy):
        check_x = grid_x + dx
        check_y = grid_y + dy
        
        if not (0 <= check_x < COLS and 0 <= check_y < ROWS):
            return False
        
        return game_map.is_walkable(check_x, check_y)
    
    def will_bomb_hit_player(self, bomb_x, bomb_y, player_x, player_y):
        if bomb_x == player_x or bomb_y == player_y:
            distance = abs(bomb_x - player_x) + abs(bomb_y - player_y)
            return distance <= self.bomb_range
        return False
    
    def can_block_player_escape(self, game_map, player, grid_x, grid_y):
        player_grid_x, player_grid_y = player.get_grid_pos()
        
        return abs(grid_x - player_grid_x) <= 2 and abs(grid_y - player_grid_y) <= 2
    
    def count_strategic_bricks(self, game_map, grid_x, grid_y):
        strategic_count = 0
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            for i in range(1, self.bomb_range + 1):
                check_x = grid_x + dx * i
                check_y = grid_y + dy * i
                
                if (0 <= check_x < COLS and 0 <= check_y < ROWS and 
                    game_map.get_tile(check_x, check_y) == TileType.BRICK):
                    strategic_count += 1
        
        return strategic_count
    
    def get_safe_direction(self, game_map, bombs):
        grid_x, grid_y = self.get_grid_pos()
        
        direction_scores = {}
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            next_x = grid_x + dx
            next_y = grid_y + dy
            
            if not (0 <= next_x < COLS and 0 <= next_y < ROWS):
                direction_scores[direction] = -1000
                continue
            if not game_map.is_walkable(next_x, next_y):
                direction_scores[direction] = -1000
                continue
            
            safety_score = self.calculate_direction_safety(game_map, bombs, next_x, next_y, direction)
            direction_scores[direction] = safety_score
        
        valid_directions = [(dir, score) for dir, score in direction_scores.items() if score > -1000]
        
        if not valid_directions:
            print(f"⚠️ {self.character} nenhuma direção válida encontrada")
            return None
        
        valid_directions.sort(key=lambda x: x[1], reverse=True)
        
        best_directions = [dir for dir, score in valid_directions[:2] if score > 0]
        
        if best_directions:
            chosen = random.choice(best_directions)
            safety_level = direction_scores[chosen]
            print(f"🎯 {self.character} direção segura escolhida: {['↑','→','↓','←'][chosen]} (segurança: {safety_level:.1f})")
            return chosen
        
        least_dangerous = valid_directions[0][0]
        print(f"⚠️ {self.character} escolheu direção menos perigosa: {['↑','→','↓','←'][least_dangerous]}")
        return least_dangerous
    
    def calculate_direction_safety(self, game_map, bombs, check_x, check_y, direction):
        safety_score = 100
        
        for bomb in bombs:
            if self.is_position_in_bomb_range(check_x, check_y, bomb):
                time_left = BOMB_TIMER - (pygame.time.get_ticks() - bomb.timer)
                if time_left < 1000:
                    safety_score -= 1000
                elif time_left < 2000:
                    safety_score -= 500
                else:
                    safety_score -= 200
        
        current_grid_x, current_grid_y = self.get_grid_pos()
        for bomb in bombs:
            current_distance = abs(current_grid_x - bomb.grid_x) + abs(current_grid_y - bomb.grid_y)
            new_distance = abs(check_x - bomb.grid_x) + abs(check_y - bomb.grid_y)
            
            if new_distance > current_distance:
                safety_score += 50
            elif new_distance < current_distance:
                safety_score -= 30
        
        dx, dy = Direction.DELTAS[direction]
        path_depth = 0
        for i in range(1, 5):
            test_x = check_x + dx * i
            test_y = check_y + dy * i
            
            if not (0 <= test_x < COLS and 0 <= test_y < ROWS):
                break
            if not game_map.is_walkable(test_x, test_y):
                break
            
            safe_in_path = True
            for bomb in bombs:
                if self.is_position_in_bomb_range(test_x, test_y, bomb):
                    safe_in_path = False
                    break
            
            if safe_in_path:
                path_depth += 1
            else:
                break
        
        safety_score += path_depth * 20
        
        if self.is_corner_position(game_map, check_x, check_y):
            safety_score -= 100
        
        if hasattr(self, 'direction'):
            opposite_direction = (self.direction + 2) % 4
            if direction == opposite_direction:
                safety_score -= 20
        
        return safety_score
    
    def is_corner_position(self, game_map, grid_x, grid_y):
        walkable_neighbors = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                check_x, check_y = grid_x + dx, grid_y + dy
                if (0 <= check_x < COLS and 0 <= check_y < ROWS and
                    game_map.is_walkable(check_x, check_y)):
                    walkable_neighbors += 1
        
        return walkable_neighbors <= 2
    
    def is_position_in_bomb_range(self, check_x, check_y, bomb):
        bomb_x, bomb_y = bomb.grid_x, bomb.grid_y
        
        if check_y == bomb_y:
            distance = abs(check_x - bomb_x)
            if distance <= bomb.explosion_range:
                return True
        
        if check_x == bomb_x:
            distance = abs(check_y - bomb_y)
            if distance <= bomb.explosion_range:
                return True
        
        return False
    
    def get_least_dangerous_direction(self, game_map, bombs, grid_x, grid_y):
        direction_danger = {}
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            danger_level = 0
            
            for bomb in bombs:
                bomb_distance = abs((grid_x + dx) - bomb.grid_x) + abs((grid_y + dy) - bomb.grid_y)
                if bomb_distance <= bomb.explosion_range:
                    danger_level += 1
            
            direction_danger[direction] = danger_level
        
        return min(direction_danger, key=direction_danger.get)
    
    def get_attack_direction(self, game_map, player):
        grid_x, grid_y = self.get_grid_pos()
        player_grid_x, player_grid_y = player.get_grid_pos()
        
        dx = player_grid_x - grid_x
        dy = player_grid_y - grid_y
        
        preferred_directions = []
        
        if abs(dx) > abs(dy):
            if dx > 0:
                preferred_directions.append(Direction.RIGHT)
            else:
                preferred_directions.append(Direction.LEFT)
            if dy > 0:
                preferred_directions.append(Direction.DOWN)
            else:
                preferred_directions.append(Direction.UP)
        else:
            if dy > 0:
                preferred_directions.append(Direction.DOWN)
            else:
                preferred_directions.append(Direction.UP)
            if dx > 0:
                preferred_directions.append(Direction.RIGHT)
            else:
                preferred_directions.append(Direction.LEFT)
        
        for direction in preferred_directions:
            dx_test, dy_test = Direction.DELTAS[direction]
            if self.is_direction_walkable(game_map, grid_x, grid_y, dx_test, dy_test):
                return direction
        
        safe_directions = []
        for direction in range(4):
            dx_test, dy_test = Direction.DELTAS[direction]
            if self.is_direction_walkable(game_map, grid_x, grid_y, dx_test, dy_test):
                safe_directions.append(direction)
        
        if safe_directions:
            opposite_direction = (self.direction + 2) % 4
            non_opposite_directions = [d for d in safe_directions if d != opposite_direction]
            if non_opposite_directions:
                return random.choice(non_opposite_directions)
            else:
                return random.choice(safe_directions)
        
        return self.direction
    
    def get_exploration_direction(self, game_map):
        grid_x, grid_y = self.get_grid_pos()
        
        direction_scores = {}
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            check_x = grid_x + dx
            check_y = grid_y + dy
            
            if not (0 <= check_x < COLS and 0 <= check_y < ROWS):
                continue
            if not game_map.is_walkable(check_x, check_y):
                continue
            
            score = 10
            
            destructible_nearby = 0
            for search_range in range(1, 4):
                search_x = check_x + dx * search_range
                search_y = check_y + dy * search_range
                
                if not (0 <= search_x < COLS and 0 <= search_y < ROWS):
                    break
                
                tile_type = game_map.get_tile(search_x, search_y)
                if tile_type == TileType.WALL:
                    break
                elif tile_type == TileType.BRICK:
                    destructible_nearby += 1
                    score += 50
                    break
            
            if hasattr(self, 'direction') and direction == self.direction:
                score += 5
            
            if hasattr(self, 'direction'):
                opposite_direction = (self.direction + 2) % 4
                if direction == opposite_direction:
                    score -= 20
            
            direction_scores[direction] = score
        
        if not direction_scores:
            return random.randint(0, 3)
        
        best_directions = [dir for dir, score in direction_scores.items() 
                          if score == max(direction_scores.values())]
        
        return random.choice(best_directions)
    
    def place_bomb(self, game_map, bombs, current_time):
        grid_x, grid_y = self.get_grid_pos()
        
        for bomb in bombs:
            if bomb.grid_x == grid_x and bomb.grid_y == grid_y:
                return False
        
        if not (0 <= grid_x < COLS and 0 <= grid_y < ROWS):
            return False
        
        try:
            new_bomb = Bomb(grid_x, grid_y, self.bomb_range, self.character)
            bombs.append(new_bomb)
            self.last_bomb_time = current_time
            return True
        except Exception as e:
            return False
    
    def update_movement(self, game_map, bombs, player, current_time):
        grid_x, grid_y = self.get_grid_pos()
        
        immediate_danger = self.assess_immediate_danger_level(bombs, current_time)
        
        if immediate_danger > 0:
            escape_direction = self.find_best_escape_direction(game_map, bombs, grid_x, grid_y, immediate_danger)
            if escape_direction is not None:
                if self.try_move_in_direction(game_map, escape_direction):
                    return
                else:
                    for alt_direction in range(4):
                        if alt_direction != escape_direction and self.is_direction_safer(game_map, bombs, alt_direction):
                            if self.try_move_in_direction(game_map, alt_direction):
                                return
        
        if hasattr(self, 'escape_mode_until') and current_time < self.escape_mode_until:
            if hasattr(self, 'escape_direction') and self.escape_direction is not None:
                if self.try_move_in_direction(game_map, self.escape_direction):
                    return
                else:
                    alternative = self.find_alternative_escape_direction(game_map, bombs)
                    if alternative is not None and self.try_move_in_direction(game_map, alternative):
                        self.escape_direction = alternative
                        return
        
        self.handle_normal_movement(game_map, bombs, current_time)
    
    def assess_immediate_danger_level(self, bombs, current_time):
        grid_x, grid_y = self.get_grid_pos()
        max_danger = 0
        
        for bomb in bombs:
            if self.is_position_in_bomb_range(grid_x, grid_y, bomb):
                time_left = BOMB_TIMER - (current_time - bomb.timer)
                distance = abs(grid_x - bomb.grid_x) + abs(grid_y - bomb.grid_y)
                
                danger_level = 0
                if time_left < 800:
                    danger_level = 3
                elif time_left < 1500:
                    danger_level = 2
                elif time_left < 2500 and distance <= 1:
                    danger_level = 2
                elif time_left < 2500:
                    danger_level = 1
                
                max_danger = max(max_danger, danger_level)
        
        return max_danger
    
    def find_best_escape_direction(self, game_map, bombs, grid_x, grid_y, danger_level):
        direction_scores = {}
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            next_x, next_y = grid_x + dx, grid_y + dy
            
            if not (0 <= next_x < COLS and 0 <= next_y < ROWS):
                continue
            if not game_map.is_walkable(next_x, next_y):
                continue
            
            score = 100
            
            for bomb in bombs:
                bomb_distance = abs(next_x - bomb.grid_x) + abs(next_y - bomb.grid_y)
                
                if self.is_position_in_bomb_range(next_x, next_y, bomb):
                    score -= 200
                else:
                    score += bomb_distance * 10
                
                if bomb.owner == self.character:
                    current_dist = abs(grid_x - bomb.grid_x) + abs(grid_y - bomb.grid_y)
                    new_dist = abs(next_x - bomb.grid_x) + abs(next_y - bomb.grid_y)
                    if new_dist > current_dist:
                        score += 50
            
            path_length = self.calculate_path_length(game_map, next_x, next_y, direction)
            score += path_length * 5
            
            direction_scores[direction] = score
        
        if not direction_scores:
            return None
        
        best_direction = max(direction_scores, key=direction_scores.get)
        return best_direction if direction_scores[best_direction] > 0 else None
    
    def calculate_path_length(self, game_map, start_x, start_y, direction):
        dx, dy = Direction.DELTAS[direction]
        length = 0
        
        for i in range(1, 5):
            check_x = start_x + dx * i
            check_y = start_y + dy * i
            
            if not (0 <= check_x < COLS and 0 <= check_y < ROWS):
                break
            if not game_map.is_walkable(check_x, check_y):
                break
                    
            length += 1
        
        return length
    
    def is_direction_safer(self, game_map, bombs, direction):
        grid_x, grid_y = self.get_grid_pos()
        dx, dy = Direction.DELTAS[direction]
        next_x, next_y = grid_x + dx, grid_y + dy
        
        if not (0 <= next_x < COLS and 0 <= next_y < ROWS):
            return False
        if not game_map.is_walkable(next_x, next_y):
            return False
        
        current_danger = 0
        new_danger = 0
        
        for bomb in bombs:
            if self.is_position_in_bomb_range(grid_x, grid_y, bomb):
                current_danger += 1
            if self.is_position_in_bomb_range(next_x, next_y, bomb):
                new_danger += 1
        
        return new_danger < current_danger
    
    def try_move_in_direction(self, game_map, direction):
        dx, dy = Direction.DELTAS[direction]
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        if game_map.can_move_to(new_x, new_y, self):
            self.x = new_x
            self.y = new_y
            self.direction = direction
            self.is_moving = True
            return True
        return False
    
    def find_alternative_escape_direction(self, game_map, bombs):
        grid_x, grid_y = self.get_grid_pos()
        
        if hasattr(self, 'escape_direction'):
            perpendicular_dirs = [(self.escape_direction + 1) % 4, (self.escape_direction + 3) % 4]
            
            for direction in perpendicular_dirs:
                if self.is_direction_safer(game_map, bombs, direction):
                    return direction
        
        for direction in range(4):
            if self.is_direction_safer(game_map, bombs, direction):
                return direction
        
        return None
    
    def handle_normal_movement(self, game_map, bombs, current_time):
        if not hasattr(self, 'last_direction_change'):
            self.last_direction_change = current_time
        
        should_change_direction = (
            current_time - self.last_direction_change > random.randint(1000, 2000) or
            not self.can_continue_current_direction(game_map, bombs)
        )
        
        if should_change_direction:
            new_direction = self.choose_smart_direction(game_map, bombs)
            if new_direction is not None:
                self.direction = new_direction
            self.last_direction_change = current_time
        
        if not self.try_move_in_direction(game_map, self.direction):
            alternative = self.choose_smart_direction(game_map, bombs)
            if alternative is not None:
                self.direction = alternative
                self.try_move_in_direction(game_map, alternative)
                self.last_direction_change = current_time
    
    def can_continue_current_direction(self, game_map, bombs):
        dx, dy = Direction.DELTAS[self.direction]
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        if not game_map.can_move_to(new_x, new_y, self):
            return False
        
        new_grid_x = int(new_x // TILE_SIZE)
        new_grid_y = int(new_y // TILE_SIZE)
        
        for bomb in bombs:
            distance = abs(new_grid_x - bomb.grid_x) + abs(new_grid_y - bomb.grid_y)
            if distance <= 2 and bomb.owner == self.character:
                return False
        
        return True
    
    def choose_smart_direction(self, game_map, bombs):
        grid_x, grid_y = self.get_grid_pos()
        direction_scores = {}
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            next_x, next_y = grid_x + dx, grid_y + dy
            
            if not (0 <= next_x < COLS and 0 <= next_y < ROWS):
                continue
            if not game_map.is_walkable(next_x, next_y):
                continue
            
            score = 50
            
            for bomb in bombs:
                distance = abs(next_x - bomb.grid_x) + abs(next_y - bomb.grid_y)
                if distance <= 3:
                    score -= (4 - distance) * 20
            
            destructible_bonus = self.count_destructible_in_direction(game_map, next_x, next_y, direction)
            score += destructible_bonus * 30
            
            path_length = self.calculate_path_length(game_map, next_x, next_y, direction)
            score += path_length * 10
            
            if direction == self.direction:
                score += 15
            
            direction_scores[direction] = score
        
        if not direction_scores:
            return None
        
        best_direction = max(direction_scores, key=direction_scores.get)
        return best_direction if direction_scores[best_direction] > 0 else None
    
    def count_destructible_in_direction(self, game_map, start_x, start_y, direction):
        dx, dy = Direction.DELTAS[direction]
        count = 0
        
        for i in range(1, 4):
            check_x = start_x + dx * i
            check_y = start_y + dy * i
            
            if not (0 <= check_x < COLS and 0 <= check_y < ROWS):
                break
            
            tile_type = game_map.get_tile(check_x, check_y)
            if tile_type == TileType.WALL:
                break
            elif tile_type == TileType.BRICK:
                count += 1
                break
        
        return count
    
    def find_safest_escape_direction(self, game_map, bombs, grid_x, grid_y):
        direction_safety = {}
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            next_x = grid_x + dx
            next_y = grid_y + dy
            
            if not (0 <= next_x < COLS and 0 <= next_y < ROWS):
                direction_safety[direction] = -1000
                continue
            if not game_map.is_walkable(next_x, next_y):
                direction_safety[direction] = -1000
                continue
            
            safety_score = 100
            
            for bomb in bombs:
                distance_to_bomb = abs(next_x - bomb.grid_x) + abs(next_y - bomb.grid_y)
                if self.is_position_in_bomb_range(next_x, next_y, bomb):
                    safety_score -= 500
                elif distance_to_bomb <= 3:
                    safety_score -= (4 - distance_to_bomb) * 50
            
            for bomb in bombs:
                if bomb.owner == self.character:
                    current_dist = abs(grid_x - bomb.grid_x) + abs(grid_y - bomb.grid_y)
                    new_dist = abs(next_x - bomb.grid_x) + abs(next_y - bomb.grid_y)
                    if new_dist > current_dist:
                        safety_score += 100
            
            direction_safety[direction] = safety_score
        
        valid_directions = [(dir, score) for dir, score in direction_safety.items() if score > -1000]
        if valid_directions:
            best_direction = max(valid_directions, key=lambda x: x[1])[0]
            return best_direction
        
        return None
    
    def choose_safe_direction(self, game_map, bombs):
        grid_x, grid_y = self.get_grid_pos()
        
        direction_scores = {}
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            next_x = grid_x + dx
            next_y = grid_y + dy
            
            if not (0 <= next_x < COLS and 0 <= next_y < ROWS):
                continue
            if not game_map.is_walkable(next_x, next_y):
                continue
            
            score = 50
            
            for bomb in bombs:
                if bomb.owner == self.character:
                    distance = abs(next_x - bomb.grid_x) + abs(next_y - bomb.grid_y)
                    if distance <= 3:
                        score -= (4 - distance) * 30
            
            if direction == self.direction:
                score += 10
            
            direction_scores[direction] = score
        
        if direction_scores:
            best_direction = max(direction_scores, key=direction_scores.get)
            return best_direction
        
        return random.randint(0, 3)
    
    def count_destructible_blocks_in_range(self, game_map, grid_x, grid_y):
        destructible_count = 0
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            
            for distance in range(1, self.bomb_range + 1):
                check_x = grid_x + dx * distance
                check_y = grid_y + dy * distance
                
                if not (0 <= check_x < COLS and 0 <= check_y < ROWS):
                    break
                
                tile_type = game_map.get_tile(check_x, check_y)
                
                if tile_type == TileType.WALL:
                    break
                
                if tile_type == TileType.BRICK:
                    destructible_count += 1
                    break
        
        return destructible_count
    
    def get_simple_escape_direction(self, game_map, bombs):
        grid_x, grid_y = self.get_grid_pos()
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            next_x = grid_x + dx
            next_y = grid_y + dy
            
            if not (0 <= next_x < COLS and 0 <= next_y < ROWS):
                continue
            if not game_map.is_walkable(next_x, next_y):
                continue
            
            is_safe = True
            for bomb in bombs:
                if self.is_position_in_bomb_range(next_x, next_y, bomb):
                    is_safe = False
                    break
            
            if is_safe:
                return direction
        
        best_direction = None
        min_danger = float('inf')
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            next_x = grid_x + dx
            next_y = grid_y + dy
            
            if not (0 <= next_x < COLS and 0 <= next_y < ROWS):
                continue
            if not game_map.is_walkable(next_x, next_y):
                continue
            
            danger = 0
            for bomb in bombs:
                if self.is_position_in_bomb_range(next_x, next_y, bomb):
                    distance = abs(next_x - bomb.grid_x) + abs(next_y - bomb.grid_y)
                    danger += (5 - distance)
            
            if danger < min_danger:
                min_danger = danger
                best_direction = direction
        
        return best_direction
    
    def move_in_direction(self, game_map, direction):
        dx, dy = Direction.DELTAS[direction]
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        if game_map.can_move_to(new_x, new_y, self):
            self.x = new_x
            self.y = new_y
            self.direction = direction
            self.is_moving = True
            return True
        return False
    
    def assess_immediate_danger(self, bombs):
        grid_x, grid_y = self.get_grid_pos()
        
        for bomb in bombs:
            if self.is_position_in_bomb_range(grid_x, grid_y, bomb):
                time_left = BOMB_TIMER - (pygame.time.get_ticks() - bomb.timer)
                if time_left < 1500:
                    return True
        
        return False
    
    def get_cautious_direction(self, game_map, bombs, player):
        grid_x, grid_y = self.get_grid_pos()
        player_grid_x, player_grid_y = player.get_grid_pos()
        
        direction_scores = {}
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            next_x = grid_x + dx
            next_y = grid_y + dy
            
            if not (0 <= next_x < COLS and 0 <= next_y < ROWS):
                continue
            if not game_map.is_walkable(next_x, next_y):
                continue
            
            score = 50
            
            for bomb in bombs:
                bomb_distance = abs(next_x - bomb.grid_x) + abs(next_y - bomb.grid_y)
                if bomb_distance <= 3:
                    score -= (4 - bomb_distance) * 20
            
            player_distance = abs(next_x - player_grid_x) + abs(next_y - player_grid_y)
            if player_distance > 6:
                score -= 10
            elif 3 <= player_distance <= 5:
                score += 20
            
            direction_scores[direction] = score
        
        if direction_scores:
            best_direction = max(direction_scores, key=direction_scores.get)
            return best_direction
        
        return random.randint(0, 3)
    
    def try_alternative_movement(self, game_map, preferred_direction):
        perpendicular_dirs = []
        opposite_dir = (preferred_direction + 2) % 4
        
        for direction in range(4):
            if direction != preferred_direction and direction != opposite_dir:
                perpendicular_dirs.append(direction)
        
        for direction in perpendicular_dirs:
            dx, dy = Direction.DELTAS[direction]
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            
            if game_map.can_move_to(new_x, new_y, self):
                self.x = new_x
                self.y = new_y
                self.direction = direction
                self.is_moving = True
                return
        
        dx, dy = Direction.DELTAS[opposite_dir]
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        if game_map.can_move_to(new_x, new_y, self):
            self.x = new_x
            self.y = new_y
            self.direction = opposite_dir
            self.is_moving = True
    
    def update_mode_intelligently(self, player, bombs, current_time):
        grid_x, grid_y = self.get_grid_pos()
        player_grid_x, player_grid_y = player.get_grid_pos()
        distance_to_player = abs(grid_x - player_grid_x) + abs(grid_y - player_grid_y)
        
        bombs_nearby = any(
            abs(bomb.grid_x - grid_x) + abs(bomb.grid_y - grid_y) <= 4 
            for bomb in bombs
        )
        
        if bombs_nearby:
            if self.mode != "flee":
                self.mode = "flee"
        elif distance_to_player <= 6:
            if random.random() < 0.1:
                self.mode = "attack"
        elif distance_to_player > 8:
            if random.random() < 0.05:
                self.mode = "explore"
    
    def find_destructible_block_nearby(self, game_map):
        grid_x, grid_y = self.get_grid_pos()
        
        adjacent_checks = [
            (grid_x + 1, grid_y, Direction.LEFT),
            (grid_x - 1, grid_y, Direction.RIGHT),
            (grid_x, grid_y + 1, Direction.UP),
            (grid_x, grid_y - 1, Direction.DOWN)
        ]
        
        for block_x, block_y, escape_dir in adjacent_checks:
            if not (0 <= block_x < COLS and 0 <= block_y < ROWS):
                continue
                
            if game_map.get_tile(block_x, block_y) == TileType.BRICK:
                escape_dx, escape_dy = Direction.DELTAS[escape_dir]
                escape_x = grid_x + escape_dx
                escape_y = grid_y + escape_dy
                
                if (0 <= escape_x < COLS and 0 <= escape_y < ROWS and 
                    game_map.is_walkable(escape_x, escape_y)):
                    
                    print(f"🎯 {self.character} encontrou bloco destrutível adjacente em ({block_x}, {block_y}) - fuga: {escape_dir}")
                    return {
                        'bomb_pos': (grid_x, grid_y),
                        'target_block': (block_x, block_y),
                        'escape_direction': escape_dir,
                        'escape_pos': (escape_x, escape_y)
                    }
        
        return None

    def get_grid_pos(self):
        return (
            int((self.x + TILE_SIZE // 2) // TILE_SIZE),
            int((self.y + TILE_SIZE // 2) // TILE_SIZE)
        )
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, TILE_SIZE, TILE_SIZE)

class Bomb:
    def __init__(self, grid_x, grid_y, explosion_range=2, owner="player"):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.x = grid_x * TILE_SIZE
        self.y = grid_y * TILE_SIZE
        self.explosion_range = explosion_range
        self.owner = owner
        self.timer = pygame.time.get_ticks()
        
        self.animation_timer = 0
        self.blinking = False
    
    def update(self, dt, game_map, player):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.timer
        
        self.animation_timer += dt
        blink_rate = max(100, 1000 - elapsed)
        self.blinking = (elapsed // blink_rate) % 2 == 0
        
        return elapsed >= BOMB_TIMER
    
    def explode(self, game_map):
        explosion_tiles = []
        
        explosion_tiles.append((self.grid_x, self.grid_y))
        game_map.set_tile(self.grid_x, self.grid_y, TileType.EXPLOSION)
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            
            for i in range(1, self.explosion_range + 1):
                x = self.grid_x + dx * i
                y = self.grid_y + dy * i
                
                if not (0 <= x < COLS and 0 <= y < ROWS):
                    break
                
                tile_type = game_map.get_tile(x, y)
                
                if tile_type == TileType.WALL:
                    break
                
                if tile_type == TileType.BRICK:
                    game_map.set_tile(x, y, TileType.EXPLOSION)
                    explosion_tiles.append((x, y))
                    if random.random() < 0.3:
                        game_map.add_powerup_at(x, y)
                    break
                
                if tile_type == TileType.EMPTY:
                    game_map.set_tile(x, y, TileType.EXPLOSION)
                    explosion_tiles.append((x, y))
        
        return Explosion(explosion_tiles, self.grid_x, self.grid_y)

class Explosion:
    def __init__(self, tiles, bomb_x, bomb_y):
        self.tiles = tiles
        self.bomb_x = bomb_x
        self.bomb_y = bomb_y
        self.timer = pygame.time.get_ticks()
        self.animation_timer = 0
        self.animation_frame = 0
    
    def update(self, dt, game_map):
        current_time = pygame.time.get_ticks()
        self.animation_timer += dt
        
        if self.animation_timer > 100:
            self.animation_frame = (self.animation_frame + 1) % 4
            self.animation_timer = 0
        
        if current_time - self.timer >= EXPLOSION_DURATION:
            for x, y in self.tiles:
                if game_map.get_tile(x, y) == TileType.EXPLOSION:
                    game_map.set_tile(x, y, TileType.EMPTY)
            return True
        
        return False

class PowerUp:
    def __init__(self, x, y, powerup_type):
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.grid_x = x
        self.grid_y = y
        self.type = powerup_type
        self.animation_timer = 0
        self.animation_frame = 0
    
    def update(self, dt):
        self.animation_timer += dt
        if self.animation_timer > 500:
            self.animation_frame = (self.animation_frame + 1) % 2
            self.animation_timer = 0
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, TILE_SIZE, TILE_SIZE)
    
    def apply_to_player(self, player):
        if self.type == TileType.POWERUP_BOMB:
            player.max_bombs += 1
        elif self.type == TileType.POWERUP_RANGE:
            player.bomb_range += 1
        elif self.type == TileType.POWERUP_SPEED:
            player.speed = min(player.speed + 0.5, 4)
    
    def apply_to_enemy(self, enemy):
        if self.type == TileType.POWERUP_BOMB:
            enemy.max_bombs += 1
            return True
        elif self.type == TileType.POWERUP_RANGE:
            enemy.bomb_range = min(enemy.bomb_range + 1, 5)
            return True
        elif self.type == TileType.POWERUP_SPEED:
            enemy.speed = min(enemy.speed + 0.3, 3.0)
            return True
        return False