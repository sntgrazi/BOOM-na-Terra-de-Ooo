
import random
from .constants import *
from .entities import PowerUp

class GameMap:
    def __init__(self, sprite_manager=None):
        self.grid = []
        self.powerups = []
        self.sprite_manager = sprite_manager
        self.init_empty_map()
    
    def init_empty_map(self):
      
        self.grid = []
        for y in range(ROWS):
            row = []
            for x in range(COLS):
                row.append(TileType.EMPTY)
            self.grid.append(row)
    
    def generate_level(self, level=1):
        
        self.powerups = []
        self.init_empty_map()
       
        if (self.sprite_manager and 
            hasattr(self.sprite_manager, 'get_theme_for_level') and
            hasattr(self.sprite_manager, 'set_map_theme')):
            
            new_theme = self.sprite_manager.get_theme_for_level(level)
            self.sprite_manager.set_map_theme(new_theme)
            print(f"🎨 Nível {level}: Usando tema '{new_theme}'")
        
        if (self.sprite_manager and 
            hasattr(self.sprite_manager, 'collision_grid') and
            self.sprite_manager.collision_grid):
            
            print("🎮 Usando sistema de 3 camadas (fundo + blocos)")
           
            for y in range(ROWS):
                for x in range(COLS):
                    if (y < len(self.sprite_manager.collision_grid) and
                        x < len(self.sprite_manager.collision_grid[y])):
                        
                        tile_type = self.sprite_manager.get_tile_type_at(x, y)
                        self.grid[y][x] = tile_type
       
            self.add_random_powerups(level)
            
        else:
           
            print("🎮 Usando geração de mapa tradicional (fallback)")
            self.generate_traditional_level(level)
    
    def generate_traditional_level(self, level=1):
      
        for y in range(ROWS):
            for x in range(COLS):
                
                if x == 0 or y == 0 or x == COLS - 1 or y == ROWS - 1:
                    self.grid[y][x] = TileType.WALL
                
                elif x % 2 == 0 and y % 2 == 0:
                    self.grid[y][x] = TileType.WALL
        
        
        brick_density = min(0.4 + level * 0.05, 0.7)
        
        for y in range(1, ROWS - 1):
            for x in range(1, COLS - 1):
                if self.grid[y][x] == TileType.EMPTY:
                    
                    if not (x <= 2 and y <= 2):
                        if random.random() < brick_density:
                            self.grid[y][x] = TileType.BRICK
        
        self.add_random_powerups(level)
    
    def add_random_powerups(self, level=1):
       
        powerup_count = min(3 + level, 8)  
        
        for _ in range(powerup_count):
          
            for attempt in range(50):  
                x = random.randint(3, COLS - 4) 
                y = random.randint(3, ROWS - 4)
                
                if self.grid[y][x] == TileType.EMPTY:
                
                    powerup_types = [TileType.POWERUP_BOMB, TileType.POWERUP_RANGE, TileType.POWERUP_SPEED]
                    powerup_type = random.choice(powerup_types)
                    
                    powerup = PowerUp(x, y, powerup_type)
                    self.powerups.append(powerup)
                    break
    
    def get_tile(self, x, y):
   
        if 0 <= x < COLS and 0 <= y < ROWS:
            return self.grid[y][x]
        return TileType.WALL  
    
    def has_clear_line_of_sight(self, x1, y1, x2, y2):
     
        grid_x1 = int(x1 // TILE_SIZE)
        grid_y1 = int(y1 // TILE_SIZE)
        grid_x2 = int(x2 // TILE_SIZE)
        grid_y2 = int(y2 // TILE_SIZE)
        
      
        if grid_x1 == grid_x2 and grid_y1 == grid_y2:
            return True
        
       
        if grid_x1 == grid_x2:  
            start_y = min(grid_y1, grid_y2)
            end_y = max(grid_y1, grid_y2)
            for y in range(start_y, end_y + 1):
                tile_type = self.get_tile(grid_x1, y)
                if tile_type in [TileType.WALL, TileType.BRICK]:
                    return False
        elif grid_y1 == grid_y2:  
            start_x = min(grid_x1, grid_x2)
            end_x = max(grid_x1, grid_x2)
            for x in range(start_x, end_x + 1):
                tile_type = self.get_tile(x, grid_y1)
                if tile_type in [TileType.WALL, TileType.BRICK]:
                    return False
        else:
          
            return True
        
        return True
    
    def can_explosion_reach_player(self, explosion_x, explosion_y, player_x, player_y):
     
        exp_grid_x = int(explosion_x // TILE_SIZE)
        exp_grid_y = int(explosion_y // TILE_SIZE)
        player_grid_x = int(player_x // TILE_SIZE)
        player_grid_y = int(player_y // TILE_SIZE)
      
        if exp_grid_x == player_grid_x and exp_grid_y == player_grid_y:
            return True
        
      
        if exp_grid_x == player_grid_x: 
            start_y = min(exp_grid_y, player_grid_y)
            end_y = max(exp_grid_y, player_grid_y)
            
       
            for y in range(start_y + 1, end_y):  
                tile_type = self.get_tile(exp_grid_x, y)
                if tile_type in [TileType.WALL, TileType.BRICK]:
                    return False  
                    
        elif exp_grid_y == player_grid_y:  
            start_x = min(exp_grid_x, player_grid_x)
            end_x = max(exp_grid_x, player_grid_x)
            
         
            for x in range(start_x + 1, end_x):  
                tile_type = self.get_tile(x, exp_grid_y)
                if tile_type in [TileType.WALL, TileType.BRICK]:
                    return False  
        else:
        
            return False
        
        return True

    def set_tile(self, x, y, tile_type):
      
        if 0 <= x < COLS and 0 <= y < ROWS:
            self.grid[y][x] = tile_type
    
    def is_walkable(self, x, y):
       
        tile = self.get_tile(x, y)
        return tile in [TileType.EMPTY, TileType.POWERUP_BOMB, 
                       TileType.POWERUP_RANGE, TileType.POWERUP_SPEED]
    
    def can_move_to(self, pixel_x, pixel_y, entity):
        
        if pixel_x < 0 or pixel_y < 0 or pixel_x >= (COLS * TILE_SIZE) - TILE_SIZE or pixel_y >= (ROWS * TILE_SIZE) - TILE_SIZE:
            return False
        
       
        corners = [
            (pixel_x, pixel_y),  
            (pixel_x + TILE_SIZE - 1, pixel_y),  
            (pixel_x, pixel_y + TILE_SIZE - 1),  
            (pixel_x + TILE_SIZE - 1, pixel_y + TILE_SIZE - 1)  
        ]
        
    
        current_grid_x = int((entity.x + TILE_SIZE // 2) // TILE_SIZE)
        current_grid_y = int((entity.y + TILE_SIZE // 2) // TILE_SIZE)
        
        
        for corner_x, corner_y in corners:
            grid_x = int(corner_x // TILE_SIZE)
            grid_y = int(corner_y // TILE_SIZE)
            
          
            if grid_x < 0 or grid_x >= COLS or grid_y < 0 or grid_y >= ROWS:
                return False
            
            target_tile = self.get_tile(grid_x, grid_y)
            
           
            if target_tile in [TileType.WALL, TileType.BRICK]:
                return False
            
           
            if target_tile == TileType.BOMB:
                
                if grid_x == current_grid_x and grid_y == current_grid_y:
                    continue
                else:
                    return False 
        
        return True
    
    def can_player_move_to(self, pixel_x, pixel_y):
       
        if pixel_x < 0 or pixel_y < 0 or pixel_x >= (COLS * TILE_SIZE) - TILE_SIZE or pixel_y >= (ROWS * TILE_SIZE) - TILE_SIZE:
            return False
        
        
        margin = TILE_SIZE // 8  
        check_points = [
            (pixel_x + margin, pixel_y + margin), 
            (pixel_x + TILE_SIZE - margin - 1, pixel_y + margin), 
            (pixel_x + margin, pixel_y + TILE_SIZE - margin - 1),  
            (pixel_x + TILE_SIZE - margin - 1, pixel_y + TILE_SIZE - margin - 1),  
            (pixel_x + TILE_SIZE // 2, pixel_y + TILE_SIZE // 2)  
        ]
        
        
        for check_x, check_y in check_points:
            grid_x = int(check_x // TILE_SIZE)
            grid_y = int(check_y // TILE_SIZE)
            
          
            if grid_x < 0 or grid_x >= COLS or grid_y < 0 or grid_y >= ROWS:
                return False
            
            target_tile = self.get_tile(grid_x, grid_y)
            
        
            if target_tile in [TileType.WALL, TileType.BRICK]:
                return False
        
        return True
    
    def add_powerup_at(self, grid_x, grid_y):
      
        powerup_types = [TileType.POWERUP_BOMB, TileType.POWERUP_RANGE, TileType.POWERUP_SPEED]
        powerup_type = random.choice(powerup_types)
        
       
        powerup = PowerUp(grid_x, grid_y, powerup_type)
        self.powerups.append(powerup)
    
    def update_powerups(self, dt, player):
       
        collected_powerups = []
        
        for i, powerup in enumerate(self.powerups):
            powerup.update(dt)
            
            
            if powerup.get_rect().colliderect(player.get_rect()):
               
                powerup.apply_to_player(player)
                collected_powerups.append(i)
        
   
        for i in reversed(collected_powerups):
            self.powerups.pop(i)
        
        return len(collected_powerups) > 0 
    
    def get_valid_spawn_positions(self, avoid_area_size=3):
        
        valid_positions = []
        
        for y in range(1, ROWS - 1):
            for x in range(1, COLS - 1):
                if (self.is_walkable(x, y) and 
                    not (x <= avoid_area_size and y <= avoid_area_size)):
                    valid_positions.append((x, y))
        
        return valid_positions

    def get_corner_spawn_positions_with_space(self, min_space=3):
     
        corner_positions = []
        
     
        corners = [
            (COLS - 2, 1),       
            (COLS - 2, ROWS - 2),   
            (1, ROWS - 2),        
            (COLS//2, 1),        
        ]
        
        for x, y in corners:
            if self.has_free_space_around(x, y, min_space):
                corner_positions.append((x, y))
                
        return corner_positions
    
    def has_free_space_around(self, center_x, center_y, min_radius):
       
        if not self.is_walkable(center_x, center_y):
            return False
            
        free_count = 0
        
       
        for dy in range(-min_radius, min_radius + 1):
            for dx in range(-min_radius, min_radius + 1):
                check_x = center_x + dx
                check_y = center_y + dy
                
             
                if 0 <= check_x < COLS and 0 <= check_y < ROWS:
                    if self.is_walkable(check_x, check_y):
                        free_count += 1
        
       
        total_area = (2 * min_radius + 1) ** 2
        return free_count >= total_area * 0.5
    
    def count_destructible_blocks(self):
        
        count = 0
        for y in range(ROWS):
            for x in range(COLS):
                if self.grid[y][x] == TileType.BRICK:
                    count += 1
        return count
    
    def render(self, surface, sprite_manager):
       
        if hasattr(sprite_manager, 'background_map') and sprite_manager.background_map:
          
            for y in range(ROWS):
                for x in range(COLS):
                    pixel_x = x * TILE_SIZE
                    pixel_y = y * TILE_SIZE
                    tile_type = self.grid[y][x]
                 
                    if tile_type == TileType.WALL:
                        sprite_manager.draw_sprite(surface, "wall", pixel_x, pixel_y)
                    elif tile_type == TileType.BRICK:
                        sprite_manager.draw_sprite(surface, "brick", pixel_x, pixel_y)
                    elif tile_type == TileType.EXPLOSION:
                        sprite_manager.draw_sprite(surface, "explosion", pixel_x, pixel_y)
        else:
          
            for y in range(ROWS):
                for x in range(COLS):
                    pixel_x = x * TILE_SIZE
                    pixel_y = y * TILE_SIZE
                    tile_type = self.grid[y][x]
                    
         
                    if tile_type == TileType.WALL:
                        sprite_manager.draw_sprite(surface, "wall", pixel_x, pixel_y)
                    elif tile_type == TileType.BRICK:
                        sprite_manager.draw_sprite(surface, "brick", pixel_x, pixel_y)
                    elif tile_type == TileType.BOMB:
                       
                        pass
                    elif tile_type == TileType.EXPLOSION:
                        sprite_manager.draw_sprite(surface, "explosion", pixel_x, pixel_y)
                   
        
     
        for powerup in self.powerups:
            powerup_name = {
                TileType.POWERUP_BOMB: "powerup_bomb",
                TileType.POWERUP_RANGE: "powerup_range", 
                TileType.POWERUP_SPEED: "powerup_speed"
            }.get(powerup.type, "powerup_bomb")
            
            sprite_manager.draw_sprite(surface, powerup_name, 
                                     powerup.x + 5, powerup.y + 5, TILE_SIZE - 10)
    
    def clear_explosions(self):
       
        for y in range(ROWS):
            for x in range(COLS):
                if self.grid[y][x] == TileType.EXPLOSION:
                    self.grid[y][x] = TileType.EMPTY
    
    def get_safe_positions_from_explosions(self, explosion_tiles):

        safe_positions = []
        
        for y in range(1, ROWS - 1):
            for x in range(1, COLS - 1):
                if self.is_walkable(x, y):
               
                    safe = True
                    for exp_x, exp_y in explosion_tiles:
                        distance = abs(x - exp_x) + abs(y - exp_y)  
                        if distance < 3:  
                            safe = False
                            break
                    
                    if safe:
                        safe_positions.append((x, y))
        
        return safe_positions


