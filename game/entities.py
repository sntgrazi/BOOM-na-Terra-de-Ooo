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
        
        # IA properties - SISTEMA ULTRA DEFENSIVO
        self.max_bombs = 1
        self.bomb_range = 2
        self.last_bomb_time = 0
        self.bomb_cooldown = random.randint(120000, 180000)  # 2-3 MINUTOS (extremamente cauteloso)
        self.spawn_time = pygame.time.get_ticks()
        self.mode = "explore"  # explore, attack, flee
        self.aggression_level = random.uniform(0.01, 0.05)  # Nível de agressividade MÍNIMO (1-5%)
        self.last_safe_position = None
        self.panic_mode = False  # Modo pânico quando detecta perigo
        
    def update(self, dt, game_map, player, bombs):
        """Atualiza o inimigo com IA"""
        if not self.alive:
            return
        
        current_time = pygame.time.get_ticks()
        
        # IA Decision Making
        self.update_ai_mode(player, bombs, current_time)
        
        # 🚀 BOMBAS QUASE NUNCA colocadas - APENAS EM SITUAÇÕES ULTRA SEGURAS
        if (current_time - self.last_bomb_time > self.bomb_cooldown and 
            current_time - self.spawn_time > 120000 and  # Só depois de 2 MINUTOS!
            not self.panic_mode):  # Nunca em modo pânico
            if self.should_place_bomb_ultra_safe(game_map, player, bombs):
                self.place_bomb(game_map, bombs, current_time)
                # Aumentar drasticamente o cooldown após colocar bomba
                self.bomb_cooldown = random.randint(180000, 300000)  # 3-5 MINUTOS
        
        # Movimento
        self.update_movement(game_map, bombs, player, current_time)
    
    def update_ai_mode(self, player, bombs, current_time):
        """Atualiza o modo da IA baseado na situação - PRIORIZA SOBREVIVÊNCIA"""
        grid_x, grid_y = self.get_grid_pos()
        
        # VERIFICAÇÃO CRÍTICA: Se há bombas próximas, SEMPRE fugir
        immediate_danger = False
        bomb_positions = []
        
        for bomb in bombs:
            bomb_positions.append((bomb.grid_x, bomb.grid_y, bomb.explosion_range))
            
            # Verificar se está em perigo IMEDIATO
            if self.is_in_bomb_explosion_path(grid_x, grid_y, bomb):
                immediate_danger = True
                break
            
            # Verificar proximidade perigosa (até 4 tiles)
            manhattan_distance = abs(bomb.grid_x - grid_x) + abs(bomb.grid_y - grid_y)
            if manhattan_distance <= 4:
                immediate_danger = True
                break
        
        # FUGA PRIORITÁRIA - Se há qualquer bomba próxima, fugir!
        if immediate_danger or len(bombs) > 0:
            self.mode = "flee"
        elif current_time - self.spawn_time < 10000:  # Primeiros 10 segundos sempre explorando
            self.mode = "explore"
        else:
            # Calcular distância do jogador
            distance_to_player = math.sqrt(
                (player.x - self.x)**2 + (player.y - self.y)**2
            )
            tile_distance = distance_to_player / TILE_SIZE
            
            # Ser MUITO cauteloso - quase sempre explorar
            if tile_distance > 8:  # Muito longe - explorar
                self.mode = "explore"
            elif tile_distance < 5:  # Perto demais - fugir
                self.mode = "flee"
            else:
                # Apenas 10% de chance de atacar
                if random.random() < 0.1:
                    self.mode = "attack"
                else:
                    self.mode = "explore"
    
    def is_in_bomb_explosion_path(self, x, y, bomb):
        """Verifica se a posição está no caminho da explosão da bomba"""
        # Mesma linha ou coluna dentro do alcance
        if ((x == bomb.grid_x and abs(y - bomb.grid_y) <= bomb.explosion_range) or
            (y == bomb.grid_y and abs(x - bomb.grid_x) <= bomb.explosion_range)):
            return True
        return False
    
    def should_place_bomb(self, game_map, player, bombs):
        """🎯 IA MAIS CAUTELOSA que coloca bombas com mais critério"""
        # Verificar se já tem muitas bombas ativas (próprias ou de outros)
        my_bombs = sum(1 for bomb in bombs if bomb.owner == self.character)
        total_bombs = len(bombs)
        
        if my_bombs >= self.max_bombs or total_bombs >= 5:  # Limitar total de bombas no mapa
            return False
        
        grid_x, grid_y = self.get_grid_pos()
        
        # 🔒 VERIFICAÇÕES DE SEGURANÇA MAIS RIGOROSAS
        # 1. Precisa ter mais de uma rota de fuga
        escape_routes = self.count_escape_routes(game_map, bombs, grid_x, grid_y)
        if escape_routes < 2:  # Exigir pelo menos 2 rotas de fuga
            return False
        
        # 2. Verificar se há outros bots muito próximos
        for bomb in bombs:
            if bomb.owner != self.character:  # Bomba de outro bot
                if abs(bomb.grid_x - grid_x) + abs(bomb.grid_y - grid_y) <= 3:
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
        """Conta quantas rotas de fuga existem"""
        escape_routes = 0
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            escape_x = grid_x + dx
            escape_y = grid_y + dy
            
            if (0 <= escape_x < COLS and 0 <= escape_y < ROWS and 
                game_map.is_walkable(escape_x, escape_y)):
                # Verificar se a rota está livre de bombas
                route_safe = True
                for bomb in bombs:
                    if (abs(bomb.grid_x - escape_x) + abs(bomb.grid_y - escape_y) <= 
                        bomb.explosion_range):
                        route_safe = False
                        break
                if route_safe:
                    escape_routes += 1
        return escape_routes
        
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
        """Retorna a direção mais segura para fugir das bombas - VERSÃO MELHORADA"""
        grid_x, grid_y = self.get_grid_pos()
        direction_safety = {}
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            safety_score = 0
            
            # Testar múltiplas posições nesta direção
            for distance in range(1, 6):  # Olhar até 5 tiles à frente
                check_x = grid_x + dx * distance
                check_y = grid_y + dy * distance
                
                # Verificar limites
                if not (0 <= check_x < COLS and 0 <= check_y < ROWS):
                    break
                
                # Verificar se é walkable
                if not game_map.is_walkable(check_x, check_y):
                    break
                
                # Calcular segurança desta posição
                position_safe = True
                for bomb in bombs:
                    # Verificar se está no caminho da explosão
                    if self.is_in_bomb_explosion_path(check_x, check_y, bomb):
                        position_safe = False
                        break
                    
                    # Penalizar proximidade com bombas
                    bomb_distance = abs(check_x - bomb.grid_x) + abs(check_y - bomb.grid_y)
                    if bomb_distance <= 4:
                        safety_score -= (5 - bomb_distance)  # Quanto mais perto, pior
                
                if position_safe:
                    safety_score += distance * 2  # Recompensar distância
                else:
                    break  # Se encontrou perigo, parar de avaliar esta direção
            
            direction_safety[direction] = safety_score
        
        # Retornar direção com maior pontuação de segurança
        if direction_safety:
            best_direction = max(direction_safety, key=direction_safety.get)
            # Se a melhor direção ainda é perigosa, escolher aleatoriamente
            if direction_safety[best_direction] > 0:
                return best_direction
        
        # Se nenhuma direção é segura, tentar qualquer direção walkable
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            check_x = grid_x + dx
            check_y = grid_y + dy
            
            if (0 <= check_x < COLS and 0 <= check_y < ROWS and 
                game_map.is_walkable(check_x, check_y)):
                return direction
        
        return random.randint(0, 3)  # Última opção
    
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
        """Retorna a direção para se aproximar do jogador estrategicamente"""
        grid_x, grid_y = self.get_grid_pos()
        player_grid_x, player_grid_y = player.get_grid_pos()
        
        # Calcular direção para o jogador
        dx = player_grid_x - grid_x
        dy = player_grid_y - grid_y
        
        # Priorizar movimento no eixo com maior diferença
        if abs(dx) > abs(dy):
            # Mover horizontalmente primeiro
            if dx > 0 and self.is_direction_walkable(game_map, grid_x, grid_y, 1, 0):
                return Direction.RIGHT
            elif dx < 0 and self.is_direction_walkable(game_map, grid_x, grid_y, -1, 0):
                return Direction.LEFT
        else:
            # Mover verticalmente primeiro
            if dy > 0 and self.is_direction_walkable(game_map, grid_x, grid_y, 0, 1):
                return Direction.DOWN
            elif dy < 0 and self.is_direction_walkable(game_map, grid_x, grid_y, 0, -1):
                return Direction.UP
        
        # Se não conseguir ir direto, escolher direção aleatória segura
        safe_directions = []
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            if self.is_direction_walkable(game_map, grid_x, grid_y, dx, dy):
                safe_directions.append(direction)
        
        return random.choice(safe_directions) if safe_directions else random.randint(0, 3)
    
    def get_exploration_direction(self, game_map):
        """Retorna direção para explorar áreas não visitadas"""
        grid_x, grid_y = self.get_grid_pos()
        exploration_directions = []
        
        for direction in range(4):
            dx, dy = Direction.DELTAS[direction]
            check_x = grid_x + dx
            check_y = grid_y + dy
            
            if (0 <= check_x < COLS and 0 <= check_y < ROWS and 
                game_map.is_walkable(check_x, check_y)):
                exploration_directions.append(direction)
        
        return random.choice(exploration_directions) if exploration_directions else random.randint(0, 3)
    
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
        """Atualiza movimento baseado na IA"""
        # Mudar direção com IA INTELIGENTE (SEM BOMBAS)
        if (current_time - self.last_direction_change > 1500 or 
            random.random() < 0.05):
            
            if self.mode == "flee":
                # 🚨 FUGA INTELIGENTE: Fugir das bombas de forma estratégica
                self.direction = self.get_safe_direction(game_map, bombs)
            elif self.mode == "attack":
                # ⚔️ ATAQUE INTELIGENTE: Se aproximar do jogador estrategicamente
                self.direction = self.get_attack_direction(game_map, player)
            else:  # explore
                # 🗺️ EXPLORAÇÃO INTELIGENTE: Explorar áreas não visitadas
                self.direction = self.get_exploration_direction(game_map)
            
            self.last_direction_change = current_time
        
        # Tentar se mover na direção atual
        dx, dy = Direction.DELTAS[self.direction]
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        # Para inimigos, usar método normal que considera bombas
        if game_map.can_move_to(new_x, new_y, self):
            self.x = new_x
            self.y = new_y
            self.is_moving = True  # 🎬 Inimigo está se movendo
        else:
            self.is_moving = False  # 🎬 Inimigo parou
            # Se não conseguir se mover, tentar outras direções
            for _ in range(4):
                test_direction = random.randint(0, 3)
                dx, dy = Direction.DELTAS[test_direction]
                test_x = self.x + dx * self.speed
                test_y = self.y + dy * self.speed
                
                if game_map.can_move_to(test_x, test_y, self):
                    self.direction = test_direction
                    self.x = test_x
                    self.y = test_y
                    self.last_direction_change = current_time
                    self.is_moving = True  # 🎬 Conseguiu se mover
                    break
    
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
        
        return Explosion(explosion_tiles)

class Explosion:
    def __init__(self, tiles):
        self.tiles = tiles
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


