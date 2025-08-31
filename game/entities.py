"""
Entidades do jogo: Jogador, Inimigos, Bombas, etc.
"""

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
        """Atualiza o jogador"""
        pass  # Não precisa mais de animação
    
    def move(self, dx, dy, game_map, bombs=None):
        """Move o jogador se possível"""
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        # USAR MÉTODO ESPECÍFICO DO JOGADOR QUE IGNORA BOMBAS
        if game_map.can_player_move_to(new_x, new_y):
            self.x = new_x
            self.y = new_y
            self.is_moving = True
            
            # Atualizar direção
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
        """Retorna a posição no grid"""
        return (
            int((self.x + TILE_SIZE // 2) // TILE_SIZE),
            int((self.y + TILE_SIZE // 2) // TILE_SIZE)
        )
    
    def get_rect(self):
        """Retorna o retângulo de colisão"""
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
        self.is_moving = False  # 🎬 Para controlar animação
        
        # IA properties - SISTEMA ULTRA-SIMPLIFICADO
        self.max_bombs = 1
        self.bomb_range = 2
        self.last_bomb_time = 0
        self.bomb_cooldown = random.randint(4000, 6000)  # 4-6 segundos
        self.spawn_time = pygame.time.get_ticks()
        self.mode = "explore"  # explore, attack
        self.last_direction_change = pygame.time.get_ticks()
        
    def update(self, dt, game_map, player, bombs):
        """Atualiza o inimigo com IA"""
        if not self.alive:
            return
        
        current_time = pygame.time.get_ticks()
        
        # IA Decision Making
        self.update_ai_mode(player, bombs, current_time)
        
        # 🚀 SISTEMA DE BOMBAS ULTRA-SIMPLIFICADO
        if (current_time - self.last_bomb_time > self.bomb_cooldown and 
            current_time - self.spawn_time > 5000):  # 5 segundos após spawn
            
            # Verificar se já tem bomba
            my_bombs = sum(1 for bomb in bombs if bomb.owner == self.character)
            if my_bombs == 0:  # Só se não tiver bomba ativa
                
                # Calcular distância do jogador
                grid_x, grid_y = self.get_grid_pos()
                player_grid_x, player_grid_y = player.get_grid_pos()
                distance = abs(grid_x - player_grid_x) + abs(grid_y - player_grid_y)
                
                # Colocar bomba se jogador estiver próximo (2-4 tiles)
                if 2 <= distance <= 4:
                    # Verificar se tem pelo menos 1 direção para escapar
                    can_escape = False
                    for direction in range(4):
                        dx, dy = Direction.DELTAS[direction]
                        test_x, test_y = grid_x + dx, grid_y + dy
                        if (0 <= test_x < COLS and 0 <= test_y < ROWS and 
                            game_map.is_walkable(test_x, test_y)):
                            can_escape = True
                            break
                    
                    if can_escape and random.random() < 0.3:  # 30% chance
                        self.place_bomb(game_map, bombs, current_time)
                        self.bomb_cooldown = random.randint(4000, 6000)  # 4-6 segundos
        
        # Movimento
        self.update_movement(game_map, bombs, player, current_time)
    
    def update_ai_mode(self, player, bombs, current_time):
        """🧠 SISTEMA DE IA ULTRA-SIMPLIFICADO"""
        # Só muda modo ocasionalmente para reduzir processamento
        if random.random() < 0.01:  # 1% chance por frame
            distance_to_player = math.sqrt(
                (player.x - self.x)**2 + (player.y - self.y)**2
            ) / TILE_SIZE
            
            if distance_to_player <= 5:
                self.mode = "attack"
            else:
                self.mode = "explore"
    
    def assess_danger_level(self, bombs, current_time):
        """Avalia o nível de perigo atual (0-3)"""
        grid_x, grid_y = self.get_grid_pos()
        max_danger = 0
        
        for bomb in bombs:
            danger = 0
            
            # Verificar se está na linha de explosão
            if self.is_position_in_bomb_range(grid_x, grid_y, bomb):
                time_left = BOMB_TIMER - (pygame.time.get_ticks() - bomb.timer)
                manhattan_distance = abs(bomb.grid_x - grid_x) + abs(bomb.grid_y - grid_y)
                
                # Calcular perigo baseado no tempo e distância
                if time_left < 1000:  # Menos de 1 segundo
                    danger = 3  # Crítico
                elif time_left < 2000:  # Menos de 2 segundos
                    danger = 2  # Alto
                elif manhattan_distance <= 1:  # Muito próximo
                    danger = 2  # Alto
                else:
                    danger = 1  # Moderado
                
                # Se é própria bomba, reduzir um pouco o perigo
                if bomb.owner == self.character and hasattr(self, 'post_bomb_grace_time'):
                    if current_time < self.post_bomb_grace_time:
                        danger = max(0, danger - 1)
            
            # Verificar proximidade geral (mesmo fora da linha de explosão)
            else:
                manhattan_distance = abs(bomb.grid_x - grid_x) + abs(bomb.grid_y - grid_y)
                if manhattan_distance <= 2 and bomb.owner != self.character:
                    danger = 1  # Perigo baixo por proximidade
            
            max_danger = max(max_danger, danger)
        
        return max_danger
    
    def calculate_distance_to_player(self, player):
        """Calcula distância até o jogador em tiles"""
        distance_pixels = math.sqrt(
            (player.x - self.x)**2 + (player.y - self.y)**2
        )
        return distance_pixels / TILE_SIZE

    def is_in_immediate_bomb_danger(self, bombs):
        """Verifica se está em perigo imediato de alguma bomba (incluindo suas próprias!)"""
        grid_x, grid_y = self.get_grid_pos()
        
        for bomb in bombs:
            # Verificar se está na linha de explosão
            if ((grid_x == bomb.grid_x and abs(grid_y - bomb.grid_y) <= bomb.explosion_range) or
                (grid_y == bomb.grid_y and abs(grid_x - bomb.grid_x) <= bomb.explosion_range)):
                
                # ⚠️ INCLUIR PRÓPRIAS BOMBAS - inimigo deve fugir das suas próprias bombas!
                return True
        return False

    def is_in_bomb_explosion_path(self, x, y, bomb):
        """Verifica se a posição está no caminho da explosão da bomba - VERSÃO INTELIGENTE"""
        # Se não está na mesma linha nem coluna, é seguro
        if x != bomb.grid_x and y != bomb.grid_y:
            return False
        
        # Calcular distância da bomba
        if x == bomb.grid_x:
            # Mesma coluna - verificar linha
            distance = abs(y - bomb.grid_y)
            if distance > bomb.explosion_range:
                return False
            
            # Verificar se há obstáculos no caminho da explosão
            min_y = min(y, bomb.grid_y)
            max_y = max(y, bomb.grid_y)
            
            # Simular explosão - verificar se algum obstáculo bloqueia
            current_y = bomb.grid_y
            step = 1 if y > bomb.grid_y else -1
            
            while current_y != y:
                current_y += step
                # Se encontrou um obstáculo antes de chegar na posição, está seguro
                if hasattr(self, '_temp_game_map'):
                    if not self._temp_game_map.is_walkable(x, current_y):
                        return False
                        
        elif y == bomb.grid_y:
            # Mesma linha - verificar coluna
            distance = abs(x - bomb.grid_x)
            if distance > bomb.explosion_range:
                return False
                
            # Verificar se há obstáculos no caminho da explosão
            current_x = bomb.grid_x
            step = 1 if x > bomb.grid_x else -1
            
            while current_x != x:
                current_x += step
                # Se encontrou um obstáculo antes de chegar na posição, está seguro
                if hasattr(self, '_temp_game_map'):
                    if not self._temp_game_map.is_walkable(current_x, y):
                        return False
        
        return True

    def should_place_bomb(self, game_map, player, bombs):
        """🎯 IA MAIS CAUTELOSA que coloca bombas com mais critério"""
        # Verificar se já tem muitas bombas ativas (próprias ou de outros)
        my_bombs = sum(1 for bomb in bombs if bomb.owner == self.character)
        total_bombs = len(bombs)
        
        if my_bombs >= self.max_bombs or total_bombs >= 5:  # Limitar total de bombas no mapa
            return False
        
        grid_x, grid_y = self.get_grid_pos()
        
        # 🔒 VERIFICAÇÕES DE SEGURANÇA MAIS RIGOROSAS
        # 1. Precisa ter pelo menos 2 rotas de fuga SEGURAS (considerando a própria bomba)
        escape_routes = self.count_escape_routes(game_map, bombs, grid_x, grid_y)
        if escape_routes < 2:  # Exigir pelo menos 2 rotas de fuga
            return False
        
        # 2. Verificação adicional: garantir que consegue sair da própria explosão
        if not self.can_escape_own_bomb(game_map, bombs, grid_x, grid_y):
            return False
        
        # 3. Verificar se há outras bombas muito próximas
        for bomb in bombs:
            if bomb.owner != self.character:  # Bomba de outro bot
                if abs(bomb.grid_x - grid_x) + abs(bomb.grid_y - grid_y) <= 4:
                    return False  # Não colocar bomba perto de outras bombas
        
        # Calcular distância do jogador
        distance_to_player = math.sqrt(
            (player.x - self.x)**2 + (player.y - self.y)**2
        )
        tile_distance = distance_to_player / TILE_SIZE
        
        # 🎯 ESTRATÉGIA 1: ATAQUE AO JOGADOR (MAIS CAUTELOSO)
        if 3 <= tile_distance <= 5:  # Distância segura
            player_grid_x, player_grid_y = player.get_grid_pos()
            
            # Verificar se jogador está na linha de explosão da bomba
            if self.will_bomb_hit_player(grid_x, grid_y, player_grid_x, player_grid_y):
                return random.random() < self.aggression_level  # Chance baseada na agressividade
        
        # � ESTRATÉGIA 2: QUEBRAR TIJOLOS (PRIORIDADE AUMENTADA)
        strategic_bricks = self.count_strategic_bricks(game_map, grid_x, grid_y)
        if strategic_bricks >= 2:
            return random.random() < 0.4  # 40% de chance
        
        # 🎲 ESTRATÉGIA 3: COMPORTAMENTO MAIS PREVISÍVEL
        return random.random() < 0.1  # Apenas 10% de chance de comportamento aleatório
    
    def should_place_bomb_aggressive(self, game_map, player, bombs):
        """🎯 SISTEMA AGRESSIVO - Coloca bombas para atacar o jogador"""
        # Verificar se já tem muitas bombas próprias
        my_bombs = sum(1 for bomb in bombs if bomb.owner == self.character)
        if my_bombs >= self.max_bombs:
            return False
        
        # Não colocar se em modo pânico extremo
        if self.panic_mode:
            return False
        
        grid_x, grid_y = self.get_grid_pos()
        player_grid_x, player_grid_y = player.get_grid_pos()
        
        # 🎯 ESTRATÉGIA 1: ATAQUE DIRETO AO JOGADOR
        distance_to_player = abs(grid_x - player_grid_x) + abs(grid_y - player_grid_y)
        
        # Se jogador está na linha de explosão E a uma distância razoável
        if 2 <= distance_to_player <= 4:
            if self.will_bomb_hit_player(grid_x, grid_y, player_grid_x, player_grid_y):
                # Verificar se tem pelo menos 1 rota de fuga
                if self.count_escape_routes(game_map, bombs, grid_x, grid_y) >= 1:
                    return random.random() < self.aggression_level * 1.5  # Chance alta de atacar
        
        # 🧱 ESTRATÉGIA 2: QUEBRAR BLOCOS PRÓXIMOS AO JOGADOR
        strategic_bricks = self.count_strategic_bricks(game_map, grid_x, grid_y)
        if strategic_bricks >= 1:  # Reduzido de 2 para 1
            # Se há blocos para quebrar E jogador está próximo
            if distance_to_player <= 5:
                if self.count_escape_routes(game_map, bombs, grid_x, grid_y) >= 1:
                    return random.random() < self.aggression_level
        
        # 🎲 ESTRATÉGIA 3: COMPORTAMENTO ALEATÓRIO AGRESSIVO
        if distance_to_player <= 3:  # Só se jogador estiver bem próximo
            if self.count_escape_routes(game_map, bombs, grid_x, grid_y) >= 2:
                return random.random() < (self.aggression_level * 0.5)  # Chance moderada
        
        return False

    def can_safely_escape_from_bomb(self, game_map, bombs, bomb_grid_x, bomb_grid_y):
        """🔍 VERIFICAÇÃO PRÉ-BOMBA: Simula se consegue escapar antes de colocar bomba - VERSÃO MAIS PERMISSIVA"""
        grid_x, grid_y = self.get_grid_pos()
        
        # Verificar se tem pelo menos 1 direção walkable imediata (requisito mínimo)
        immediate_exits = 0
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            check_x = grid_x + dx
            check_y = grid_y + dy
            
            # Verificar se a primeira posição é válida e walkable
            if (0 <= check_x < COLS and 0 <= check_y < ROWS and 
                game_map.is_walkable(check_x, check_y)):
                immediate_exits += 1
        
        # Se não tem nem uma saída imediata, é muito perigoso
        if immediate_exits == 0:
            return False
        
        # Criar bomba simulada para testar escape mais detalhado
        simulated_bomb = type('obj', (object,), {
            'grid_x': bomb_grid_x,
            'grid_y': bomb_grid_y,
            'owner': self.character,
            'explosion_range': 2  # Range padrão
        })
        
        # Lista de bombas incluindo a simulada
        test_bombs = list(bombs) + [simulated_bomb]
        
        # Testar se consegue escapar em pelo menos 1 direção
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            
            # Testar fuga nesta direção por até 3 tiles (mais permissivo)
            for distance in range(1, 4):
                check_x = grid_x + dx * distance
                check_y = grid_y + dy * distance
                
                # Verificar limites
                if not (0 <= check_x < COLS and 0 <= check_y < ROWS):
                    break
                
                # Verificar se é walkable
                if not game_map.is_walkable(check_x, check_y):
                    break
                
                # Verificar se esta posição é segura da bomba simulada
                safe_from_simulated_bomb = not self.is_in_bomb_explosion_path(check_x, check_y, simulated_bomb)
                
                if safe_from_simulated_bomb:
                    # Se consegue chegar a uma posição segura, é suficiente
                    return True
        
        # Se chegou aqui, não conseguiu encontrar escape - mas ainda permitir se tiver saídas imediatas
        return immediate_exits >= 2  # Pelo menos 2 saídas imediatas

    def should_place_bomb_smart(self, game_map, player, bombs):
        """🧠 SISTEMA INTELIGENTE MELHORADO - IA estratégica para colocação de bombas"""
        # Verificar se já tem muitas bombas próprias
        my_bombs = sum(1 for bomb in bombs if bomb.owner == self.character)
        if my_bombs >= self.max_bombs:
            return False
        
        # NUNCA colocar se em pânico (muito próximo de explosão)
        if self.panic_mode:
            return False
        
        grid_x, grid_y = self.get_grid_pos()
        player_grid_x, player_grid_y = player.get_grid_pos()
        
        # 🎯 ESTRATÉGIA 1: ATACAR O JOGADOR (Prioridade máxima)
        distance_to_player = abs(grid_x - player_grid_x) + abs(grid_y - player_grid_y)
        
        # Se o jogador está na linha de fogo e a uma distância boa para atacar
        if 2 <= distance_to_player <= 5:
            if self.will_bomb_hit_player(grid_x, grid_y, player_grid_x, player_grid_y):
                # Verificar se tem pelo menos 2 rotas de fuga seguras
                escape_routes = self.calculate_escape_routes(game_map, bombs, grid_x, grid_y)
                if len(escape_routes) >= 2:
                    print(f"🎯 {self.character} vai atacar o jogador! Distância: {distance_to_player}")
                    return random.random() < 0.7  # 70% chance de atacar
        
        # 🎯 ESTRATÉGIA 2: QUEBRAR BLOCOS DESTRUTÍVEIS (Segunda prioridade)
        destructible_info = self.find_best_destructible_target(game_map)
        if destructible_info:
            # Verificar se a posição é segura para colocar bomba
            escape_routes = self.calculate_escape_routes(game_map, bombs, grid_x, grid_y)
            if len(escape_routes) >= 1:
                print(f"💎 {self.character} vai quebrar bloco destrutível!")
                return random.random() < 0.5  # 50% chance de quebrar blocos
        
        # 🎯 ESTRATÉGIA 3: POSICIONAMENTO TÁTICO (Terceira prioridade)
        # Colocar bomba para controlar território ou bloquear passagens do jogador
        if distance_to_player >= 4:  # Não muito próximo do jogador
            if self.is_tactical_position(game_map, player, grid_x, grid_y):
                escape_routes = self.calculate_escape_routes(game_map, bombs, grid_x, grid_y)
                if len(escape_routes) >= 2:
                    print(f"🛡️ {self.character} posicionamento tático!")
                    return random.random() < 0.3  # 30% chance tática
        
        return False
    
    def calculate_escape_routes(self, game_map, bombs, bomb_x, bomb_y):
        """Calcula todas as rotas de fuga possíveis de uma posição"""
        escape_routes = []
        
        # Simular bomba na posição atual
        future_bombs = list(bombs)
        simulated_bomb = type('obj', (object,), {
            'grid_x': bomb_x,
            'grid_y': bomb_y,
            'explosion_range': self.bomb_range,
            'owner': self.character
        })()
        future_bombs.append(simulated_bomb)
        
        # Testar cada direção
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            
            # Verificar se consegue escapar nesta direção
            for distance in range(1, 4):  # Testar até 3 tiles de distância
                escape_x = bomb_x + dx * distance
                escape_y = bomb_y + dy * distance
                
                # Verificar limites
                if not (0 <= escape_x < COLS and 0 <= escape_y < ROWS):
                    break
                
                # Verificar se o caminho está livre
                if not game_map.is_walkable(escape_x, escape_y):
                    break
                
                # Verificar se esta posição está segura de todas as bombas
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
                    break  # Encontrou rota segura nesta direção
        
        return escape_routes
    
    def find_best_destructible_target(self, game_map):
        """Encontra o melhor bloco destrutível para atacar"""
        grid_x, grid_y = self.get_grid_pos()
        best_target = None
        max_value = 0
        
        # Verificar blocos destrutíveis no alcance da bomba
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            for distance in range(1, self.bomb_range + 1):
                target_x = grid_x + dx * distance
                target_y = grid_y + dy * distance
                
                # Verificar limites
                if not (0 <= target_x < COLS and 0 <= target_y < ROWS):
                    break
                
                tile_type = game_map.get_tile(target_x, target_y)
                
                # Se encontrou parede, parar nesta direção
                if tile_type == TileType.WALL:
                    break
                
                # Se encontrou bloco destrutível, avaliar valor
                if tile_type == TileType.BRICK:
                    # Calcular valor baseado na posição estratégica
                    value = self.calculate_destructible_value(game_map, target_x, target_y)
                    if value > max_value:
                        max_value = value
                        best_target = {
                            'position': (target_x, target_y),
                            'value': value,
                            'direction': direction
                        }
                    break  # Parar nesta direção após encontrar bloco
        
        return best_target
    
    def calculate_destructible_value(self, game_map, block_x, block_y):
        """Calcula o valor estratégico de destruir um bloco"""
        value = 1  # Valor base
        
        # Maior valor se estiver perto das bordas (abre mais espaço)
        distance_to_edge = min(block_x, block_y, COLS - 1 - block_x, ROWS - 1 - block_y)
        if distance_to_edge <= 2:
            value += 2
        
        # Maior valor se houver mais blocos destrutíveis próximos
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
        """Verifica se a posição atual é boa para colocação tática de bomba"""
        player_grid_x, player_grid_y = player.get_grid_pos()
        
        # Verificar se está numa passagem que o jogador pode usar
        if self.is_in_player_path(game_map, player, grid_x, grid_y):
            return True
        
        # Verificar se está numa posição central (controle de território)
        center_x, center_y = COLS // 2, ROWS // 2
        distance_to_center = abs(grid_x - center_x) + abs(grid_y - center_y)
        if distance_to_center <= 3:
            return True
        
        return False
    
    def is_in_player_path(self, game_map, player, grid_x, grid_y):
        """Verifica se está numa possível rota do jogador"""
        player_grid_x, player_grid_y = player.get_grid_pos()
        
        # Verificar se está na mesma linha ou coluna do jogador
        if grid_x == player_grid_x or grid_y == player_grid_y:
            return True
        
        # Verificar se está numa passagem estreita
        walkable_neighbors = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                check_x, check_y = grid_x + dx, grid_y + dy
                if (0 <= check_x < COLS and 0 <= check_y < ROWS and
                    game_map.is_walkable(check_x, check_y)):
                    walkable_neighbors += 1
        
        # Se tem poucos vizinhos caminháveis, é uma passagem estratégica
        return walkable_neighbors <= 3
    
    def should_place_bomb_simple(self, game_map, player, bombs):
        """🎯 SISTEMA SIMPLIFICADO - Decisões rápidas de bomba"""
        # Verificar se já tem bomba ativa
        my_bombs = sum(1 for bomb in bombs if bomb.owner == self.character)
        if my_bombs >= self.max_bombs:
            return False
        
        grid_x, grid_y = self.get_grid_pos()
        player_grid_x, player_grid_y = player.get_grid_pos()
        
        # Não colocar se muito próximo das bordas
        if grid_x <= 1 or grid_y <= 1 or grid_x >= COLS-2 or grid_y >= ROWS-2:
            return False
        
        # Verificar se tem pelo menos 2 direções para escapar
        escape_directions = 0
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            test_x, test_y = grid_x + dx, grid_y + dy
            
            if (0 <= test_x < COLS and 0 <= test_y < ROWS and 
                game_map.is_walkable(test_x, test_y)):
                # Verificar se esta direção está segura de outras bombas
                safe_from_bombs = True
                for bomb in bombs:
                    if self.is_position_in_bomb_range(test_x, test_y, bomb):
                        safe_from_bombs = False
                        break
                if safe_from_bombs:
                    escape_directions += 1
        
        if escape_directions < 2:
            return False  # Precisa de pelo menos 2 rotas de fuga
        
        # Calcular distância do jogador
        distance_to_player = abs(grid_x - player_grid_x) + abs(grid_y - player_grid_y)
        
        # Estratégia 1: Atacar jogador se estiver na linha de fogo
        if 2 <= distance_to_player <= 4:
            if (grid_x == player_grid_x or grid_y == player_grid_y):
                return random.random() < 0.6  # 60% chance de atacar
        
        # Estratégia 2: Quebrar blocos destrutíveis próximos
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
            return random.random() < 0.4  # 40% chance de quebrar blocos
        
        # Estratégia 3: Colocação aleatória ocasional
        if distance_to_player >= 5:  # Longe do jogador
            return random.random() < 0.1  # 10% chance aleatória
        
        return False

    def can_safely_escape_own_bomb(self, game_map, bombs, grid_x, grid_y):
        """Verifica se pode escapar com segurança de sua própria bomba"""
        # Simular explosão da bomba na posição atual
        explosion_range = self.bomb_range
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            
            # Verificar se pode correr pelo menos 3-4 tiles nesta direção
            safe_distance = 0
            for i in range(1, explosion_range + 3):  # Além do alcance da bomba
                check_x = grid_x + dx * i
                check_y = grid_y + dy * i
                
                if not (0 <= check_x < COLS and 0 <= check_y < ROWS):
                    break
                if not game_map.is_walkable(check_x, check_y):
                    break
                
                safe_distance += 1
            
            # Se consegue correr pelo menos 3 tiles, é seguro
            if safe_distance >= 3:
                return True
        
        return False

    def has_long_escape_route(self, game_map, bombs, grid_x, grid_y):
        """Verifica se tem rota de fuga longa (não apenas 1 tile)"""
        long_routes = 0
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            route_length = 0
            
            for i in range(1, 6):  # Verificar até 5 tiles
                check_x = grid_x + dx * i
                check_y = grid_y + dy * i
                
                if not (0 <= check_x < COLS and 0 <= check_y < ROWS):
                    break
                if not game_map.is_walkable(check_x, check_y):
                    break
                
                # Verificar se não há bombas próximas nesta rota
                safe_from_bombs = True
                for bomb in bombs:
                    if abs(bomb.grid_x - check_x) + abs(bomb.grid_y - check_y) <= bomb.explosion_range + 1:
                        safe_from_bombs = False
                        break
                
                if not safe_from_bombs:
                    break
                
                route_length += 1
            
            # Rota longa = pelo menos 3 tiles livres
            if route_length >= 3:
                long_routes += 1
        
        return long_routes >= 1  # Pelo menos 1 rota longa

    def should_place_bomb_ultra_safe(self, game_map, player, bombs):
        """🛡️ SISTEMA ULTRA DEFENSIVO - Quase nunca coloca bombas"""
        # ❌ NUNCA colocar se há QUALQUER bomba no mapa
        if len(bombs) > 0:
            return False
        
        # ❌ NUNCA colocar se em modo pânico
        if self.panic_mode:
            return False
        
        # ❌ NUNCA colocar se já tem bomba própria
        my_bombs = sum(1 for bomb in bombs if bomb.owner == self.character)
        if my_bombs >= self.max_bombs:
            return False
        
        grid_x, grid_y = self.get_grid_pos()
        
        # ❌ NUNCA colocar se não tiver pelo menos 8 rotas de fuga totalmente seguras
        safe_routes = 0
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            
            # Verificar até 8 tiles na direção para garantir fuga
            route_completely_safe = True
            for distance in range(1, 9):
                check_x = grid_x + dx * distance
                check_y = grid_y + dy * distance
                
                if not (0 <= check_x < COLS and 0 <= check_y < ROWS):
                    break
                if not game_map.is_walkable(check_x, check_y):
                    route_completely_safe = False
                    break
                    
                # Verificar se player está muito perto desta rota
                distance_to_player = abs(check_x - player.get_grid_pos()[0]) + abs(check_y - player.get_grid_pos()[1])
                if distance_to_player <= 2:  # Player muito perto
                    route_completely_safe = False
                    break
            
            if route_completely_safe and distance >= 6:  # Rota longa e segura
                safe_routes += 1
        
        # ❌ Precisa de pelo menos 3 rotas ultra seguras
        if safe_routes < 3:
            return False
        
        # ❌ NUNCA atacar se player estiver perto (menos de 8 tiles)
        distance_to_player = math.sqrt(
            (player.x - self.x)**2 + (player.y - self.y)**2
        )
        tile_distance = distance_to_player / TILE_SIZE
        
        if tile_distance < 8:
            return False
        
        # ❌ Apenas 1% de chance FINAL mesmo com todas as condições perfeitas
        return random.random() < 0.01
    
    def count_escape_routes(self, game_map, bombs, grid_x, grid_y):
        """Conta quantas rotas de fuga SEGURAS existem considerando a bomba que será colocada"""
        escape_routes = 0
        
        # Simular a bomba que será colocada nesta posição
        future_bombs = bombs + [type('', (), {
            'grid_x': grid_x, 
            'grid_y': grid_y, 
            'explosion_range': self.bomb_range,
            'owner': self.character
        })()]
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            
            # Verificar se consegue escapar a pelo menos 3 tiles de distância
            escape_possible = False
            for escape_distance in range(1, 4):  # Tentar escapar 1, 2 ou 3 tiles
                escape_x = grid_x + dx * escape_distance
                escape_y = grid_y + dy * escape_distance
                
                # Verificar limites
                if not (0 <= escape_x < COLS and 0 <= escape_y < ROWS):
                    break
                
                # Verificar se o caminho está livre
                if not game_map.is_walkable(escape_x, escape_y):
                    break
                
                # Verificar se esta posição de escape está segura de TODAS as bombas
                position_safe = True
                for bomb in future_bombs:
                    # Verificar se está na linha de explosão da bomba
                    if ((bomb.grid_x == escape_x and abs(bomb.grid_y - escape_y) <= bomb.explosion_range) or
                        (bomb.grid_y == escape_y and abs(bomb.grid_x - escape_x) <= bomb.explosion_range)):
                        position_safe = False
                        break
                
                if position_safe:
                    escape_possible = True
                    break  # Encontrou uma posição segura nesta direção
            
            if escape_possible:
                escape_routes += 1
                
        return escape_routes

    def can_escape_own_bomb(self, game_map, bombs, grid_x, grid_y):
        """Verifica se consegue escapar da própria bomba considerando tempo de fuga"""
        # Simular movimento: em 3 segundos (BOMB_TIMER), consegue se mover ~6 tiles
        # Ser mais conservador: assumir que consegue mover apenas 4 tiles
        max_escape_tiles = 4
        
        # Testar fuga em todas as direções
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            
            # Verificar se consegue chegar a uma posição segura
            for distance in range(1, max_escape_tiles + 1):
                escape_x = grid_x + dx * distance
                escape_y = grid_y + dy * distance
                
                # Verificar limites
                if not (0 <= escape_x < COLS and 0 <= escape_y < ROWS):
                    break
                
                # Verificar se o caminho está livre (sem obstáculos para chegar lá)
                path_clear = True
                for step in range(1, distance + 1):
                    check_x = grid_x + dx * step
                    check_y = grid_y + dy * step
                    if not game_map.is_walkable(check_x, check_y):
                        path_clear = False
                        break
                
                if not path_clear:
                    break
                
                # Verificar se esta posição final estará segura da própria bomba
                if not ((grid_x == escape_x and abs(grid_y - escape_y) <= self.bomb_range) or
                        (grid_y == escape_y and abs(grid_x - escape_x) <= self.bomb_range)):
                    # Posição segura encontrada! Verificar se também está segura de outras bombas
                    safe_from_others = True
                    for bomb in bombs:
                        if ((bomb.grid_x == escape_x and abs(bomb.grid_y - escape_y) <= bomb.explosion_range) or
                            (bomb.grid_y == escape_y and abs(bomb.grid_x - escape_x) <= bomb.explosion_range)):
                            safe_from_others = False
                            break
                    
                    if safe_from_others:
                        return True  # Encontrou uma rota de fuga segura!
        
        return False  # Não encontrou rota de fuga segura
        
        return False
    
    def has_any_escape_route(self, game_map, bombs, grid_x, grid_y):
        """🔒 VERIFICAÇÃO ULTRA INTELIGENTE de rota de fuga - simula movimento futuro"""
        # Simular onde o bot estará quando a bomba explodir (3 segundos)
        # Bot pode se mover até 3 tiles em 3 segundos
        max_escape_distance = 3
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            
            # Verificar múltiplas posições de fuga (1, 2 e 3 tiles de distância)
            for distance in range(1, max_escape_distance + 1):
                escape_x = grid_x + dx * distance
                escape_y = grid_y + dy * distance
                
                # Verificar limites
                if not (0 <= escape_x < COLS and 0 <= escape_y < ROWS):
                    break
                
                # Verificar se é walkable
                if not game_map.is_walkable(escape_x, escape_y):
                    break
                
                # Verificar se há bombas próximas que podem matar o inimigo nesta posição
                bomb_danger = False
                for bomb in bombs:
                    bomb_distance = abs(escape_x - bomb.grid_x) + abs(escape_y - bomb.grid_y)
                    if bomb_distance <= bomb.explosion_range:
                        bomb_danger = True
                        break
                
                # Se encontrou uma posição segura, verificar se consegue chegar lá
                if not bomb_danger:
                    # Verificar se o caminho até lá é livre
                    path_clear = True
                    for step in range(1, distance):
                        path_x = grid_x + dx * step
                        path_y = grid_y + dy * step
                        if not game_map.is_walkable(path_x, path_y):
                            path_clear = False
                            break
                    
                    if path_clear:
                        return True  # Encontrou rota de fuga segura!
        
        return False  # Nenhuma rota de fuga segura encontrada
    
    def is_direction_walkable(self, game_map, grid_x, grid_y, dx, dy):
        """Verifica se uma direção é walkable (simples)"""
        check_x = grid_x + dx
        check_y = grid_y + dy
        
        # Verificar limites
        if not (0 <= check_x < COLS and 0 <= check_y < ROWS):
            return False
        
        # Verificar se é walkable
        return game_map.is_walkable(check_x, check_y)
    
    def will_bomb_hit_player(self, bomb_x, bomb_y, player_x, player_y):
        """Verifica se uma bomba vai atingir o jogador"""
        # Mesmo eixo horizontal ou vertical
        if bomb_x == player_x or bomb_y == player_y:
            # Calcular distância Manhattan
            distance = abs(bomb_x - player_x) + abs(bomb_y - player_y)
            return distance <= self.bomb_range
        return False
    
    def can_block_player_escape(self, game_map, player, grid_x, grid_y):
        """Verifica se pode bloquear uma rota de fuga do jogador"""
        player_grid_x, player_grid_y = player.get_grid_pos()
        
        # Verificar se está entre o jogador e uma saída
        # (implementação simplificada)
        return abs(grid_x - player_grid_x) <= 2 and abs(grid_y - player_grid_y) <= 2
    
    def count_strategic_bricks(self, game_map, grid_x, grid_y):
        """Conta tijolos estratégicos ao redor"""
        strategic_count = 0
        
        # Verificar tijolos em linha reta (formato da explosão)
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
        """🏃 SISTEMA INTELIGENTE DE FUGA - Encontra a melhor direção para escapar"""
        grid_x, grid_y = self.get_grid_pos()
        
        # Avaliar cada direção com pontuação de segurança
        direction_scores = {}
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            next_x = grid_x + dx
            next_y = grid_y + dy
            
            # Verificar se é válido
            if not (0 <= next_x < COLS and 0 <= next_y < ROWS):
                direction_scores[direction] = -1000  # Direção inválida
                continue
            if not game_map.is_walkable(next_x, next_y):
                direction_scores[direction] = -1000  # Direção bloqueada
                continue
            
            # Calcular pontuação de segurança
            safety_score = self.calculate_direction_safety(game_map, bombs, next_x, next_y, direction)
            direction_scores[direction] = safety_score
        
        # Filtrar direções válidas
        valid_directions = [(dir, score) for dir, score in direction_scores.items() if score > -1000]
        
        if not valid_directions:
            print(f"⚠️ {self.character} nenhuma direção válida encontrada")
            return None
        
        # Ordenar por segurança (maior pontuação = mais seguro)
        valid_directions.sort(key=lambda x: x[1], reverse=True)
        
        # Escolher entre as melhores direções (top 2) para adicionar variabilidade
        best_directions = [dir for dir, score in valid_directions[:2] if score > 0]
        
        if best_directions:
            chosen = random.choice(best_directions)
            safety_level = direction_scores[chosen]
            print(f"🎯 {self.character} direção segura escolhida: {['↑','→','↓','←'][chosen]} (segurança: {safety_level:.1f})")
            return chosen
        
        # Se não há direções completamente seguras, escolher a menos perigosa
        least_dangerous = valid_directions[0][0]
        print(f"⚠️ {self.character} escolheu direção menos perigosa: {['↑','→','↓','←'][least_dangerous]}")
        return least_dangerous
    
    def calculate_direction_safety(self, game_map, bombs, check_x, check_y, direction):
        """Calcula a pontuação de segurança de uma direção específica"""
        safety_score = 100  # Pontuação base
        
        # 1. Verificar perigo imediato de bombas
        for bomb in bombs:
            if self.is_position_in_bomb_range(check_x, check_y, bomb):
                # Penalizar baseado no tempo restante da bomba
                time_left = BOMB_TIMER - (pygame.time.get_ticks() - bomb.timer)
                if time_left < 1000:  # Menos de 1 segundo
                    safety_score -= 1000  # Muito perigoso
                elif time_left < 2000:  # Menos de 2 segundos
                    safety_score -= 500   # Perigoso
                else:
                    safety_score -= 200   # Moderadamente perigoso
        
        # 2. Verificar se a direção leva para mais longe das bombas
        current_grid_x, current_grid_y = self.get_grid_pos()
        for bomb in bombs:
            current_distance = abs(current_grid_x - bomb.grid_x) + abs(current_grid_y - bomb.grid_y)
            new_distance = abs(check_x - bomb.grid_x) + abs(check_y - bomb.grid_y)
            
            if new_distance > current_distance:
                safety_score += 50  # Bônus por se afastar da bomba
            elif new_distance < current_distance:
                safety_score -= 30  # Penalidade por se aproximar da bomba
        
        # 3. Verificar profundidade do caminho (quantos tiles pode avançar nesta direção)
        dx, dy = Direction.DELTAS[direction]
        path_depth = 0
        for i in range(1, 5):  # Verificar até 4 tiles à frente
            test_x = check_x + dx * i
            test_y = check_y + dy * i
            
            if not (0 <= test_x < COLS and 0 <= test_y < ROWS):
                break
            if not game_map.is_walkable(test_x, test_y):
                break
            
            # Verificar se há bombas neste caminho
            safe_in_path = True
            for bomb in bombs:
                if self.is_position_in_bomb_range(test_x, test_y, bomb):
                    safe_in_path = False
                    break
            
            if safe_in_path:
                path_depth += 1
            else:
                break
        
        # Bônus por ter caminho longo e seguro
        safety_score += path_depth * 20
        
        # 4. Evitar ficar preso em cantos
        if self.is_corner_position(game_map, check_x, check_y):
            safety_score -= 100
        
        # 5. Preferir não voltar na direção oposta (evitar oscilação)
        if hasattr(self, 'direction'):
            opposite_direction = (self.direction + 2) % 4
            if direction == opposite_direction:
                safety_score -= 20
        
        return safety_score
    
    def is_corner_position(self, game_map, grid_x, grid_y):
        """Verifica se uma posição é um canto (poucas saídas)"""
        walkable_neighbors = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                check_x, check_y = grid_x + dx, grid_y + dy
                if (0 <= check_x < COLS and 0 <= check_y < ROWS and
                    game_map.is_walkable(check_x, check_y)):
                    walkable_neighbors += 1
        
        return walkable_neighbors <= 2  # 2 ou menos vizinhos = canto
    
    def is_position_in_bomb_range(self, check_x, check_y, bomb):
        """Versão simples: verifica se posição está no alcance de uma bomba"""
        bomb_x, bomb_y = bomb.grid_x, bomb.grid_y
        
        # Verificar se está na mesma linha (horizontal)
        if check_y == bomb_y:
            distance = abs(check_x - bomb_x)
            if distance <= bomb.explosion_range:
                return True
        
        # Verificar se está na mesma coluna (vertical)  
        if check_x == bomb_x:
            distance = abs(check_y - bomb_y)
            if distance <= bomb.explosion_range:
                return True
        
        return False
    
    def get_least_dangerous_direction(self, game_map, bombs, grid_x, grid_y):
        """Retorna a direção com menos bombas próximas"""
        direction_danger = {}
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            danger_level = 0
            
            for bomb in bombs:
                bomb_distance = abs((grid_x + dx) - bomb.grid_x) + abs((grid_y + dy) - bomb.grid_y)
                if bomb_distance <= bomb.explosion_range:
                    danger_level += 1
            
            direction_danger[direction] = danger_level
        
        # Retornar direção com menor perigo
        return min(direction_danger, key=direction_danger.get)
    
    def get_attack_direction(self, game_map, player):
        """Retorna a direção para se aproximar do jogador estrategicamente com pathfinding"""
        grid_x, grid_y = self.get_grid_pos()
        player_grid_x, player_grid_y = player.get_grid_pos()
        
        # Calcular direção para o jogador
        dx = player_grid_x - grid_x
        dy = player_grid_y - grid_y
        
        # Lista de direções priorizadas baseadas na distância ao jogador
        preferred_directions = []
        
        # Priorizar movimento no eixo com maior diferença
        if abs(dx) > abs(dy):
            # Mover horizontalmente primeiro
            if dx > 0:
                preferred_directions.append(Direction.RIGHT)
            else:
                preferred_directions.append(Direction.LEFT)
            # Depois verticalmente
            if dy > 0:
                preferred_directions.append(Direction.DOWN)
            else:
                preferred_directions.append(Direction.UP)
        else:
            # Mover verticalmente primeiro
            if dy > 0:
                preferred_directions.append(Direction.DOWN)
            else:
                preferred_directions.append(Direction.UP)
            # Depois horizontalmente
            if dx > 0:
                preferred_directions.append(Direction.RIGHT)
            else:
                preferred_directions.append(Direction.LEFT)
        
        # Testar direções na ordem de preferência
        for direction in preferred_directions:
            dx_test, dy_test = Direction.DELTAS[direction]
            if self.is_direction_walkable(game_map, grid_x, grid_y, dx_test, dy_test):
                return direction
        
        # Se nenhuma direção preferida funcionou, tentar qualquer direção disponível
        safe_directions = []
        for direction in range(4):
            dx_test, dy_test = Direction.DELTAS[direction]
            if self.is_direction_walkable(game_map, grid_x, grid_y, dx_test, dy_test):
                safe_directions.append(direction)
        
        # Preferir direções que não sejam opostas à direção atual (evitar ficar oscilando)
        if safe_directions:
            opposite_direction = (self.direction + 2) % 4
            non_opposite_directions = [d for d in safe_directions if d != opposite_direction]
            if non_opposite_directions:
                return random.choice(non_opposite_directions)
            else:
                return random.choice(safe_directions)
        
        return self.direction  # Manter direção atual se não há alternativas
    
    def get_exploration_direction(self, game_map):
        """Retorna direção para explorar - versão simplificada"""
        grid_x, grid_y = self.get_grid_pos()
        
        # Buscar direções válidas
        valid_directions = []
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            check_x = grid_x + dx
            check_y = grid_y + dy
            
            if (0 <= check_x < COLS and 0 <= check_y < ROWS and 
                game_map.is_walkable(check_x, check_y)):
                valid_directions.append(direction)
        
        if not valid_directions:
            return random.randint(0, 3)  # Fallback
        
        # 50% chance de continuar na direção atual se possível
        if (hasattr(self, 'direction') and 
            self.direction in valid_directions and 
            random.random() < 0.5):
            return self.direction
        
        # Evitar direção oposta (reduz oscilação)
        if hasattr(self, 'direction'):
            opposite_direction = (self.direction + 2) % 4
            non_opposite = [d for d in valid_directions if d != opposite_direction]
            if non_opposite:
                return random.choice(non_opposite)
        
        return random.choice(valid_directions)
    
    def place_bomb(self, game_map, bombs, current_time):
        """Coloca uma bomba"""
        grid_x, grid_y = self.get_grid_pos()
        
        # Verificar se já existe bomba nesta posição
        for bomb in bombs:
            if bomb.grid_x == grid_x and bomb.grid_y == grid_y:
                return False
        
        # Criar nova bomba (NÃO definir como sólida no mapa ainda!)
        new_bomb = Bomb(grid_x, grid_y, self.bomb_range, self.character)
        bombs.append(new_bomb)
        # game_map.set_tile(grid_x, grid_y, TileType.BOMB)  # REMOVIDO - deixar fantasma
        
        self.last_bomb_time = current_time
        return True
    
        
    def update_movement(self, game_map, bombs, player, current_time):
        """🚀 SISTEMA DE MOVIMENTO ULTRA-SIMPLIFICADO"""
        # 1. Verificar se há bomba muito próxima (perigo real)
        grid_x, grid_y = self.get_grid_pos()
        in_danger = False
        
        for bomb in bombs:
            if self.is_position_in_bomb_range(grid_x, grid_y, bomb):
                time_left = BOMB_TIMER - (pygame.time.get_ticks() - bomb.timer)
                if time_left < 1000:  # Menos de 1 segundo
                    in_danger = True
                    break
        
        # 2. Se em perigo, mover para qualquer direção segura
        if in_danger:
            for direction in range(4):
                dx, dy = Direction.DELTAS[direction]
                new_x = self.x + dx * self.speed
                new_y = self.y + dy * self.speed
                
                if game_map.can_move_to(new_x, new_y, self):
                    # Verificar se esta nova posição é segura
                    new_grid_x = int(new_x // TILE_SIZE)
                    new_grid_y = int(new_y // TILE_SIZE)
                    
                    safe = True
                    for bomb in bombs:
                        if self.is_position_in_bomb_range(new_grid_x, new_grid_y, bomb):
                            safe = False
                            break
                    
                    if safe:
                        self.x = new_x
                        self.y = new_y
                        self.direction = direction
                        self.is_moving = True
                        return
        
        # 3. Movimento normal - muito simples
        # Mudar direção ocasionalmente
        if not hasattr(self, 'last_direction_change'):
            self.last_direction_change = current_time
        
        if current_time - self.last_direction_change > random.randint(1000, 3000):
            # Escolher nova direção aleatória
            self.direction = random.randint(0, 3)
            self.last_direction_change = current_time
        
        # Tentar mover na direção atual
        dx, dy = Direction.DELTAS[self.direction]
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        if game_map.can_move_to(new_x, new_y, self):
            self.x = new_x
            self.y = new_y
            self.is_moving = True
        else:
            # Se não consegue mover, escolher nova direção imediatamente
            valid_directions = []
            for direction in range(4):
                test_dx, test_dy = Direction.DELTAS[direction]
                test_x = self.x + test_dx * self.speed
                test_y = self.y + test_dy * self.speed
                
                if game_map.can_move_to(test_x, test_y, self):
                    valid_directions.append(direction)
            
            if valid_directions:
                self.direction = random.choice(valid_directions)
                dx, dy = Direction.DELTAS[self.direction]
                new_x = self.x + dx * self.speed
                new_y = self.y + dy * self.speed
                
                self.x = new_x
                self.y = new_y
                self.is_moving = True
                self.last_direction_change = current_time
    
    def get_simple_escape_direction(self, game_map, bombs):
        """Encontra direção de escape simples e rápida"""
        grid_x, grid_y = self.get_grid_pos()
        
        # Testar todas as direções
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            next_x = grid_x + dx
            next_y = grid_y + dy
            
            # Verificar se é válido e walkable
            if not (0 <= next_x < COLS and 0 <= next_y < ROWS):
                continue
            if not game_map.is_walkable(next_x, next_y):
                continue
            
            # Verificar se está seguro de bombas
            is_safe = True
            for bomb in bombs:
                if self.is_position_in_bomb_range(next_x, next_y, bomb):
                    is_safe = False
                    break
            
            if is_safe:
                return direction
        
        # Se nenhuma direção é completamente segura, escolher a menos perigosa
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
            
            # Calcular nível de perigo
            danger = 0
            for bomb in bombs:
                if self.is_position_in_bomb_range(next_x, next_y, bomb):
                    distance = abs(next_x - bomb.grid_x) + abs(next_y - bomb.grid_y)
                    danger += (5 - distance)  # Quanto mais próximo, mais perigoso
            
            if danger < min_danger:
                min_danger = danger
                best_direction = direction
        
        return best_direction
    
    def move_in_direction(self, game_map, direction):
        """Move o inimigo na direção especificada"""
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
        """Avalia se há perigo imediato de explosão"""
        grid_x, grid_y = self.get_grid_pos()
        
        for bomb in bombs:
            if self.is_position_in_bomb_range(grid_x, grid_y, bomb):
                # Verificar tempo restante da bomba
                time_left = BOMB_TIMER - (pygame.time.get_ticks() - bomb.timer)
                if time_left < 1500:  # Apenas menos de 1.5 segundos = perigo REAL
                    return True
        
        return False
    
    def get_cautious_direction(self, game_map, bombs, player):
        """Movimento cauteloso que evita bombas mas não foge completamente"""
        grid_x, grid_y = self.get_grid_pos()
        player_grid_x, player_grid_y = player.get_grid_pos()
        
        # Avaliar direções baseado em segurança e distância do jogador
        direction_scores = {}
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            next_x = grid_x + dx
            next_y = grid_y + dy
            
            if not (0 <= next_x < COLS and 0 <= next_y < ROWS):
                continue
            if not game_map.is_walkable(next_x, next_y):
                continue
            
            score = 50  # Score base
            
            # Penalizar proximidade com bombas
            for bomb in bombs:
                bomb_distance = abs(next_x - bomb.grid_x) + abs(next_y - bomb.grid_y)
                if bomb_distance <= 3:
                    score -= (4 - bomb_distance) * 20
            
            # Não se afastar muito do jogador (manter pressão)
            player_distance = abs(next_x - player_grid_x) + abs(next_y - player_grid_y)
            if player_distance > 6:
                score -= 10
            elif 3 <= player_distance <= 5:
                score += 20  # Distância ideal
            
            direction_scores[direction] = score
        
        # Escolher melhor direção
        if direction_scores:
            best_direction = max(direction_scores, key=direction_scores.get)
            return best_direction
        
        return random.randint(0, 3)  # Fallback
    
    def try_alternative_movement(self, game_map, preferred_direction):
        """Tenta movimentos alternativos quando a direção preferida está bloqueada"""
        # Tentar direções perpendiculares primeiro (evitar voltar)
        perpendicular_dirs = []
        opposite_dir = (preferred_direction + 2) % 4
        
        for direction in range(4):
            if direction != preferred_direction and direction != opposite_dir:
                perpendicular_dirs.append(direction)
        
        # Tentar direções perpendiculares
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
        
        # Como último recurso, tentar direção oposta
        dx, dy = Direction.DELTAS[opposite_dir]
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        if game_map.can_move_to(new_x, new_y, self):
            self.x = new_x
            self.y = new_y
            self.direction = opposite_dir
            self.is_moving = True
    
    def update_mode_intelligently(self, player, bombs, current_time):
        """Atualiza o modo do inimigo baseado na situação atual"""
        grid_x, grid_y = self.get_grid_pos()
        player_grid_x, player_grid_y = player.get_grid_pos()
        distance_to_player = abs(grid_x - player_grid_x) + abs(grid_y - player_grid_y)
        
        # Verificar se há bombas próximas
        bombs_nearby = any(
            abs(bomb.grid_x - grid_x) + abs(bomb.grid_y - grid_y) <= 4 
            for bomb in bombs
        )
        
        # Lógica de mudança de modo
        if bombs_nearby:
            if self.mode != "flee":
                self.mode = "flee"
        elif distance_to_player <= 6:
            if random.random() < 0.1:  # 10% chance de mudar para ataque
                self.mode = "attack"
        elif distance_to_player > 8:
            if random.random() < 0.05:  # 5% chance de explorar
                self.mode = "explore"
    def find_destructible_block_nearby(self, game_map):
        """Encontra blocos destrutíveis adjacentes e garante fuga segura SIMPLES"""
        grid_x, grid_y = self.get_grid_pos()
        
        # Verificar posições adjacentes para blocos destrutíveis
        adjacent_checks = [
            (grid_x + 1, grid_y, Direction.LEFT),    # bloco à direita, fuga à esquerda  
            (grid_x - 1, grid_y, Direction.RIGHT),   # bloco à esquerda, fuga à direita
            (grid_x, grid_y + 1, Direction.UP),      # bloco abaixo, fuga acima
            (grid_x, grid_y - 1, Direction.DOWN)     # bloco acima, fuga abaixo
        ]
        
        for block_x, block_y, escape_dir in adjacent_checks:
            # Verificar se o bloco destrutível existe e está nos limites
            if not (0 <= block_x < COLS and 0 <= block_y < ROWS):
                continue
                
            # Verificar se há bloco destrutível nesta posição
            if game_map.get_tile(block_x, block_y) == TileType.BRICK:
                # Calcular posição de fuga (1 tile na direção de escape)
                escape_dx, escape_dy = Direction.DELTAS[escape_dir]
                escape_x = grid_x + escape_dx
                escape_y = grid_y + escape_dy
                
                # Verificar se posição de fuga está nos limites e é walkable
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
        """Retorna a posição no grid"""
        return (
            int((self.x + TILE_SIZE // 2) // TILE_SIZE),
            int((self.y + TILE_SIZE // 2) // TILE_SIZE)
        )
    
    def get_rect(self):
        """Retorna o retângulo de colisão"""
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
        
        # Animação
        self.animation_timer = 0
        self.blinking = False
    
    def update(self, dt, game_map, player):
        """Atualiza a bomba"""
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.timer
        
        # Animação de piscar
        self.animation_timer += dt
        blink_rate = max(100, 1000 - elapsed)
        self.blinking = (elapsed // blink_rate) % 2 == 0
        
        # Verificar se é hora de explodir
        return elapsed >= BOMB_TIMER
    
    def explode(self, game_map):
        """Cria uma explosão"""
        explosion_tiles = []
        
        # Centro da explosão
        explosion_tiles.append((self.grid_x, self.grid_y))
        game_map.set_tile(self.grid_x, self.grid_y, TileType.EXPLOSION)
        
        # Expandir nas 4 direções
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            
            for i in range(1, self.explosion_range + 1):
                x = self.grid_x + dx * i
                y = self.grid_y + dy * i
                
                # Verificar limites
                if not (0 <= x < COLS and 0 <= y < ROWS):
                    break
                
                tile_type = game_map.get_tile(x, y)
                
                # PARAR IMEDIATAMENTE na parede (não atravessar)
                if tile_type == TileType.WALL:
                    break
                
                # Destruir tijolo e parar COMPLETAMENTE
                if tile_type == TileType.BRICK:
                    game_map.set_tile(x, y, TileType.EXPLOSION)
                    explosion_tiles.append((x, y))
                    # Chance de criar power-up
                    if random.random() < 0.3:
                        game_map.add_powerup_at(x, y)
                    break  # ⛔ PARAR AQUI - não continuar além do bloco destrutível
                
                # Adicionar à explosão (apenas se for espaço vazio)
                if tile_type == TileType.EMPTY:
                    game_map.set_tile(x, y, TileType.EXPLOSION)
                    explosion_tiles.append((x, y))
        
        return Explosion(explosion_tiles, self.grid_x, self.grid_y)

class Explosion:
    def __init__(self, tiles, bomb_x, bomb_y):
        self.tiles = tiles
        self.bomb_x = bomb_x  # Posição original da bomba
        self.bomb_y = bomb_y  # Posição original da bomba
        self.timer = pygame.time.get_ticks()
        self.animation_timer = 0
        self.animation_frame = 0
    
    def update(self, dt, game_map):
        """Atualiza a explosão"""
        current_time = pygame.time.get_ticks()
        self.animation_timer += dt
        
        if self.animation_timer > 100:  # Animação rápida
            self.animation_frame = (self.animation_frame + 1) % 4
            self.animation_timer = 0
        
        # Verificar se a explosão acabou
        if current_time - self.timer >= EXPLOSION_DURATION:
            # Remover explosão do mapa
            for x, y in self.tiles:
                if game_map.get_tile(x, y) == TileType.EXPLOSION:
                    game_map.set_tile(x, y, TileType.EMPTY)
            return True  # Explosão terminada
        
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
        """Atualiza o power-up"""
        self.animation_timer += dt
        if self.animation_timer > 500:  # Animação lenta
            self.animation_frame = (self.animation_frame + 1) % 2
            self.animation_timer = 0
    
    def get_rect(self):
        """Retorna o retângulo de colisão"""
        return pygame.Rect(self.x, self.y, TILE_SIZE, TILE_SIZE)
    
    def apply_to_player(self, player):
        """Aplica o efeito do power-up ao jogador"""
        if self.type == TileType.POWERUP_BOMB:
            player.max_bombs += 1
        elif self.type == TileType.POWERUP_RANGE:
            player.bomb_range += 1
        elif self.type == TileType.POWERUP_SPEED:
            player.speed = min(player.speed + 0.5, 4)  # Limite máximo de velocidade


