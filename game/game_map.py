"""
Sistema de mapa para o Bomberman
Gerencia o grid do jogo, colisões e power-ups
"""

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
        """Inicializa um mapa vazio"""
        self.grid = []
        for y in range(ROWS):
            row = []
            for x in range(COLS):
                row.append(TileType.EMPTY)
            self.grid.append(row)
    
    def generate_level(self, level=1):
        """Gera um nível do jogo usando o sistema de 3 camadas com temas"""
        self.powerups = []
        self.init_empty_map()
        
        # 🎨 ALTERAR TEMA DO MAPA BASEADO NO NÍVEL
        if (self.sprite_manager and 
            hasattr(self.sprite_manager, 'get_theme_for_level') and
            hasattr(self.sprite_manager, 'set_map_theme')):
            
            new_theme = self.sprite_manager.get_theme_for_level(level)
            self.sprite_manager.set_map_theme(new_theme)
            print(f"🎨 Nível {level}: Usando tema '{new_theme}'")
        
        # 🗺️ Se temos sprite_manager com grid de colisão, usar ele
        if (self.sprite_manager and 
            hasattr(self.sprite_manager, 'collision_grid') and
            self.sprite_manager.collision_grid):
            
            print("🎮 Usando sistema de 3 camadas (fundo + blocos)")
            
            # Copiar grid de colisão do sprite_manager
            for y in range(ROWS):
                for x in range(COLS):
                    if (y < len(self.sprite_manager.collision_grid) and
                        x < len(self.sprite_manager.collision_grid[y])):
                        
                        tile_type = self.sprite_manager.get_tile_type_at(x, y)
                        self.grid[y][x] = tile_type
            
            # Adicionar power-ups em blocos destrutíveis
            self.add_random_powerups(level)
            
        else:
            # Fallback: gerar mapa tradicional se não há sprite_manager
            print("🎮 Usando geração de mapa tradicional (fallback)")
            self.generate_traditional_level(level)
    
    def generate_traditional_level(self, level=1):
        """Gera mapa tradicional como fallback"""
        # Colocar paredes nas bordas
        for y in range(ROWS):
            for x in range(COLS):
                # Bordas do mapa
                if x == 0 or y == 0 or x == COLS - 1 or y == ROWS - 1:
                    self.grid[y][x] = TileType.WALL
                # Paredes internas em padrão
                elif x % 2 == 0 and y % 2 == 0:
                    self.grid[y][x] = TileType.WALL
        
        # Adicionar tijolos aleatórios
        brick_density = min(0.4 + level * 0.05, 0.7)
        
        for y in range(1, ROWS - 1):
            for x in range(1, COLS - 1):
                if self.grid[y][x] == TileType.EMPTY:
                    # Não colocar tijolos muito perto da posição inicial do jogador
                    if not (x <= 2 and y <= 2):
                        if random.random() < brick_density:
                            self.grid[y][x] = TileType.BRICK
        
        self.add_random_powerups(level)
    
    def add_random_powerups(self, level=1):
        """Adiciona power-ups aleatórios em posições livres"""
        powerup_count = min(3 + level, 8)  # 3-8 power-ups por nível
        
        for _ in range(powerup_count):
            # Encontrar uma posição livre aleatória
            for attempt in range(50):  # Máximo 50 tentativas
                x = random.randint(3, COLS - 4)  # Evitar bordas e spawn do jogador
                y = random.randint(3, ROWS - 4)
                
                if self.grid[y][x] == TileType.EMPTY:
                    # Escolher tipo de power-up aleatório
                    powerup_types = [TileType.POWERUP_BOMB, TileType.POWERUP_RANGE, TileType.POWERUP_SPEED]
                    powerup_type = random.choice(powerup_types)
                    
                    powerup = PowerUp(x, y, powerup_type)
                    self.powerups.append(powerup)
                    break
    
    def get_tile(self, x, y):
        """Retorna o tipo de tile na posição especificada"""
        if 0 <= x < COLS and 0 <= y < ROWS:
            return self.grid[y][x]
        return TileType.WALL  # Fora dos limites é considerado parede
    
    def has_clear_line_of_sight(self, x1, y1, x2, y2):
        """Verifica se há linha de visão clara entre duas posições (sem blocos sólidos)"""
        # Converter posições de pixel para grid
        grid_x1 = int(x1 // TILE_SIZE)
        grid_y1 = int(y1 // TILE_SIZE)
        grid_x2 = int(x2 // TILE_SIZE)
        grid_y2 = int(y2 // TILE_SIZE)
        
        # Se estão no mesmo tile, sempre há linha de visão
        if grid_x1 == grid_x2 and grid_y1 == grid_y2:
            return True
        
        # Algoritmo simples: verificar se há blocos sólidos adjacentes
        # Para movimentos ortogonais simples
        if grid_x1 == grid_x2:  # Movimento vertical
            start_y = min(grid_y1, grid_y2)
            end_y = max(grid_y1, grid_y2)
            for y in range(start_y, end_y + 1):
                tile_type = self.get_tile(grid_x1, y)
                if tile_type in [TileType.WALL, TileType.BRICK]:
                    return False
        elif grid_y1 == grid_y2:  # Movimento horizontal
            start_x = min(grid_x1, grid_x2)
            end_x = max(grid_x1, grid_x2)
            for x in range(start_x, end_x + 1):
                tile_type = self.get_tile(x, grid_y1)
                if tile_type in [TileType.WALL, TileType.BRICK]:
                    return False
        else:
            # Para movimentos diagonais, verificar se há blocos adjacentes que bloqueiam
            # Este é um caso mais complexo - por simplicidade, consideramos que tiles adjacentes não bloqueiam colisão direta
            return True
        
        return True
    
    def can_explosion_reach_player(self, explosion_x, explosion_y, player_x, player_y):
        """Verifica se uma explosão pode atingir um jogador considerando obstáculos"""
        # Converter posições de pixel para grid
        exp_grid_x = int(explosion_x // TILE_SIZE)
        exp_grid_y = int(explosion_y // TILE_SIZE)
        player_grid_x = int(player_x // TILE_SIZE)
        player_grid_y = int(player_y // TILE_SIZE)
        
        # Se estão no mesmo tile, sempre atinge
        if exp_grid_x == player_grid_x and exp_grid_y == player_grid_y:
            return True
        
        # Verificar se estão na mesma linha ou coluna (explosão em cruz)
        if exp_grid_x == player_grid_x:  # Mesma coluna
            start_y = min(exp_grid_y, player_grid_y)
            end_y = max(exp_grid_y, player_grid_y)
            
            # Verificar se há blocos sólidos no caminho
            for y in range(start_y + 1, end_y):  # Não incluir origem e destino
                tile_type = self.get_tile(exp_grid_x, y)
                if tile_type in [TileType.WALL, TileType.BRICK]:
                    return False  # Bloqueado por obstáculo
                    
        elif exp_grid_y == player_grid_y:  # Mesma linha
            start_x = min(exp_grid_x, player_grid_x)
            end_x = max(exp_grid_x, player_grid_x)
            
            # Verificar se há blocos sólidos no caminho
            for x in range(start_x + 1, end_x):  # Não incluir origem e destino
                tile_type = self.get_tile(x, exp_grid_y)
                if tile_type in [TileType.WALL, TileType.BRICK]:
                    return False  # Bloqueado por obstáculo
        else:
            # Não está na mesma linha nem coluna, explosão não atinge
            return False
        
        return True

    def set_tile(self, x, y, tile_type):
        """Define o tipo de tile na posição especificada"""
        if 0 <= x < COLS and 0 <= y < ROWS:
            self.grid[y][x] = tile_type
    
    def is_walkable(self, x, y):
        """Verifica se uma posição é caminhável"""
        tile = self.get_tile(x, y)
        return tile in [TileType.EMPTY, TileType.POWERUP_BOMB, 
                       TileType.POWERUP_RANGE, TileType.POWERUP_SPEED]
    
    def can_move_to(self, pixel_x, pixel_y, entity):
        """Verifica se uma entidade pode se mover para a posição em pixels"""
        # Verificar limites em pixels primeiro
        if pixel_x < 0 or pixel_y < 0 or pixel_x >= (COLS * TILE_SIZE) - TILE_SIZE or pixel_y >= (ROWS * TILE_SIZE) - TILE_SIZE:
            return False
        
        # Verificar os 4 cantos da entidade na nova posição
        corners = [
            (pixel_x, pixel_y),  # Canto superior esquerdo
            (pixel_x + TILE_SIZE - 1, pixel_y),  # Canto superior direito
            (pixel_x, pixel_y + TILE_SIZE - 1),  # Canto inferior esquerdo
            (pixel_x + TILE_SIZE - 1, pixel_y + TILE_SIZE - 1)  # Canto inferior direito
        ]
        
        # Obter posição atual da entidade no grid
        current_grid_x = int((entity.x + TILE_SIZE // 2) // TILE_SIZE)
        current_grid_y = int((entity.y + TILE_SIZE // 2) // TILE_SIZE)
        
        # Verificar cada canto
        for corner_x, corner_y in corners:
            grid_x = int(corner_x // TILE_SIZE)
            grid_y = int(corner_y // TILE_SIZE)
            
            # Verificar limites do grid
            if grid_x < 0 or grid_x >= COLS or grid_y < 0 or grid_y >= ROWS:
                return False
            
            target_tile = self.get_tile(grid_x, grid_y)
            
            # Tiles sólidos bloqueiam movimento
            if target_tile in [TileType.WALL, TileType.BRICK]:
                return False
            
            # Tratamento especial para bombas
            if target_tile == TileType.BOMB:
                # Se é a posição atual, permitir (para sair da bomba)
                if grid_x == current_grid_x and grid_y == current_grid_y:
                    continue
                else:
                    return False  # Não pode entrar em outra bomba
        
        return True
    
    def can_player_move_to(self, pixel_x, pixel_y):
        """Verifica se o JOGADOR pode se mover - IGNORA BOMBAS E EXPLOSÕES"""
        # Verificar limites em pixels primeiro
        if pixel_x < 0 or pixel_y < 0 or pixel_x >= (COLS * TILE_SIZE) - TILE_SIZE or pixel_y >= (ROWS * TILE_SIZE) - TILE_SIZE:
            return False
        
        # Verificar uma área menor no centro da entidade (75% do tamanho)
        margin = TILE_SIZE // 8  # Margem de 12.5% de cada lado
        check_points = [
            (pixel_x + margin, pixel_y + margin),  # Canto superior esquerdo interno
            (pixel_x + TILE_SIZE - margin - 1, pixel_y + margin),  # Canto superior direito interno
            (pixel_x + margin, pixel_y + TILE_SIZE - margin - 1),  # Canto inferior esquerdo interno
            (pixel_x + TILE_SIZE - margin - 1, pixel_y + TILE_SIZE - margin - 1),  # Canto inferior direito interno
            (pixel_x + TILE_SIZE // 2, pixel_y + TILE_SIZE // 2)  # Centro
        ]
        
        # Verificar cada ponto
        for check_x, check_y in check_points:
            grid_x = int(check_x // TILE_SIZE)
            grid_y = int(check_y // TILE_SIZE)
            
            # Verificar limites do grid
            if grid_x < 0 or grid_x >= COLS or grid_y < 0 or grid_y >= ROWS:
                return False
            
            target_tile = self.get_tile(grid_x, grid_y)
            
            # APENAS paredes e tijolos bloqueiam o jogador
            if target_tile in [TileType.WALL, TileType.BRICK]:
                return False
        
        return True
    
    def add_powerup_at(self, grid_x, grid_y):
        """Adiciona um power-up na posição especificada"""
        # Escolher tipo de power-up aleatório
        powerup_types = [TileType.POWERUP_BOMB, TileType.POWERUP_RANGE, TileType.POWERUP_SPEED]
        powerup_type = random.choice(powerup_types)
        
        # Criar power-up
        powerup = PowerUp(grid_x, grid_y, powerup_type)
        self.powerups.append(powerup)
    
    def update_powerups(self, dt, player):
        """Atualiza power-ups e verifica colisões com o jogador"""
        collected_powerups = []
        
        for i, powerup in enumerate(self.powerups):
            powerup.update(dt)
            
            # Verificar colisão com jogador
            if powerup.get_rect().colliderect(player.get_rect()):
                # Aplicar efeito do power-up
                powerup.apply_to_player(player)
                collected_powerups.append(i)
        
        # Remover power-ups coletados (em ordem reversa para não afetar os índices)
        for i in reversed(collected_powerups):
            self.powerups.pop(i)
        
        return len(collected_powerups) > 0  # Retorna True se coletou algum power-up
    
    def get_valid_spawn_positions(self, avoid_area_size=3):
        """Retorna posições válidas para spawn de inimigos"""
        valid_positions = []
        
        for y in range(1, ROWS - 1):
            for x in range(1, COLS - 1):
                if (self.is_walkable(x, y) and 
                    not (x <= avoid_area_size and y <= avoid_area_size)):
                    valid_positions.append((x, y))
        
        return valid_positions

    def get_corner_spawn_positions_with_space(self, min_space=3):
        """Retorna posições nos cantos com pelo menos min_space blocos livres ao redor"""
        corner_positions = []
        
        # Definir cantos estratégicos
        corners = [
            (COLS - 2, 1),         # Canto superior direito
            (COLS - 2, ROWS - 2),  # Canto inferior direito  
            (1, ROWS - 2),         # Canto inferior esquerdo
            (COLS//2, 1),          # Centro superior
        ]
        
        for x, y in corners:
            if self.has_free_space_around(x, y, min_space):
                corner_positions.append((x, y))
                
        return corner_positions
    
    def has_free_space_around(self, center_x, center_y, min_radius):
        """Verifica se há pelo menos min_radius blocos livres ao redor da posição"""
        if not self.is_walkable(center_x, center_y):
            return False
            
        free_count = 0
        
        # Verificar área ao redor
        for dy in range(-min_radius, min_radius + 1):
            for dx in range(-min_radius, min_radius + 1):
                check_x = center_x + dx
                check_y = center_y + dy
                
                # Verificar limites
                if 0 <= check_x < COLS and 0 <= check_y < ROWS:
                    if self.is_walkable(check_x, check_y):
                        free_count += 1
        
        # Precisa de pelo menos metade dos blocos livres na área
        total_area = (2 * min_radius + 1) ** 2
        return free_count >= total_area * 0.5
    
    def count_destructible_blocks(self):
        """Conta quantos blocos destrutíveis existem no mapa"""
        count = 0
        for y in range(ROWS):
            for x in range(COLS):
                if self.grid[y][x] == TileType.BRICK:
                    count += 1
        return count
    
    def render(self, surface, sprite_manager):
        """Renderiza o mapa na tela com sistema de camadas"""
        # Se estamos usando o sistema de 3 camadas, desenhar apenas os blocos
        if hasattr(sprite_manager, 'background_map') and sprite_manager.background_map:
            # Renderizar apenas blocos estruturais e destrutíveis
            for y in range(ROWS):
                for x in range(COLS):
                    pixel_x = x * TILE_SIZE
                    pixel_y = y * TILE_SIZE
                    tile_type = self.grid[y][x]
                    
                    # Renderizar blocos sobre o fundo
                    if tile_type == TileType.WALL:
                        sprite_manager.draw_sprite(surface, "wall", pixel_x, pixel_y)
                    elif tile_type == TileType.BRICK:
                        sprite_manager.draw_sprite(surface, "brick", pixel_x, pixel_y)
                    elif tile_type == TileType.EXPLOSION:
                        sprite_manager.draw_sprite(surface, "explosion", pixel_x, pixel_y)
        else:
            # Renderização tradicional completa (fallback)
            for y in range(ROWS):
                for x in range(COLS):
                    pixel_x = x * TILE_SIZE
                    pixel_y = y * TILE_SIZE
                    tile_type = self.grid[y][x]
                    
                    # Renderizar tile baseado no tipo
                    if tile_type == TileType.WALL:
                        sprite_manager.draw_sprite(surface, "wall", pixel_x, pixel_y)
                    elif tile_type == TileType.BRICK:
                        sprite_manager.draw_sprite(surface, "brick", pixel_x, pixel_y)
                    elif tile_type == TileType.BOMB:
                        # Bombas são renderizadas separadamente
                        pass
                    elif tile_type == TileType.EXPLOSION:
                        sprite_manager.draw_sprite(surface, "explosion", pixel_x, pixel_y)
                    # TileType.EMPTY não precisa renderizar nada
        
        # Renderizar power-ups sempre
        for powerup in self.powerups:
            powerup_name = {
                TileType.POWERUP_BOMB: "powerup_bomb",
                TileType.POWERUP_RANGE: "powerup_range", 
                TileType.POWERUP_SPEED: "powerup_speed"
            }.get(powerup.type, "powerup_bomb")
            
            sprite_manager.draw_sprite(surface, powerup_name, 
                                     powerup.x + 5, powerup.y + 5, TILE_SIZE - 10)
    
    def clear_explosions(self):
        """Remove todas as explosões do mapa"""
        for y in range(ROWS):
            for x in range(COLS):
                if self.grid[y][x] == TileType.EXPLOSION:
                    self.grid[y][x] = TileType.EMPTY
    
    def get_safe_positions_from_explosions(self, explosion_tiles):
        """Retorna posições seguras longe das explosões"""
        safe_positions = []
        
        for y in range(1, ROWS - 1):
            for x in range(1, COLS - 1):
                if self.is_walkable(x, y):
                    # Verificar se está longe das explosões
                    safe = True
                    for exp_x, exp_y in explosion_tiles:
                        distance = abs(x - exp_x) + abs(y - exp_y)  # Distância Manhattan
                        if distance < 3:  # Muito perto da explosão
                            safe = False
                            break
                    
                    if safe:
                        safe_positions.append((x, y))
        
        return safe_positions


