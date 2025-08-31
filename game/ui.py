

import pygame
import math
from .constants import *

class UI:
    def __init__(self, screen):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        
        self.gradient_colors = [
            (255, 107, 107),  
            (78, 205, 196),   
            (69, 183, 209),   
            (150, 206, 180)   
        ]
        self.gradient_offset = 0
    
    def update(self, dt):
       
        self.gradient_offset += dt * 0.001  
    
    def draw_gradient_background(self, colors=None):
        
        if colors is None:
            colors = self.gradient_colors
        
        
        for y in range(SCREEN_HEIGHT):
            
            progress = (y / SCREEN_HEIGHT + self.gradient_offset) % 1.0
            color_index = int(progress * len(colors))
            next_color_index = (color_index + 1) % len(colors)
            
            
            blend = (progress * len(colors)) % 1.0
            color1 = colors[color_index]
            color2 = colors[next_color_index]
            
            r = int(color1[0] * (1 - blend) + color2[0] * blend)
            g = int(color1[1] * (1 - blend) + color2[1] * blend)
            b = int(color1[2] * (1 - blend) + color2[2] * blend)
            
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    
    def draw_text_with_shadow(self, text, font, color, shadow_color, x, y, center=False):
       
        shadow_surface = font.render(text, True, shadow_color)
        shadow_rect = shadow_surface.get_rect()
        if center:
            shadow_rect.center = (x + 2, y + 2)
        else:
            shadow_rect.topleft = (x + 2, y + 2)
        self.screen.blit(shadow_surface, shadow_rect)
        
        
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)
        
        return text_rect
    
    def draw_button(self, text, x, y, width, height, active=False):
        
        if active:
            button_color = (255, 69, 0)  
            text_color = Colors.WHITE
        else:
            button_color = (255, 71, 87)  
            text_color = Colors.WHITE
        
    
        button_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, button_color, button_rect)
        pygame.draw.rect(self.screen, Colors.BLACK, button_rect, 3)
        
      
        if active:
            pygame.draw.rect(self.screen, (255, 255, 255, 100), button_rect, 2)
        
       
        text_rect = self.draw_text_with_shadow(
            text, self.font_medium, text_color, Colors.BLACK,
            x + width // 2, y + height // 2, center=True
        )
        
        return button_rect
    
    def draw_start_screen(self):
        
        self.draw_gradient_background()
        
        # Título principal com símbolos ASCII
        title_y = SCREEN_HEIGHT // 4
        self.draw_text_with_shadow(
            "*** BOMBERMAN ***", self.font_large, Colors.YELLOW, Colors.BLACK,
            SCREEN_WIDTH // 2, title_y, center=True
        )
        
        # Subtítulo
        self.draw_text_with_shadow(
            "~ Hora de Aventura Edition ~", self.font_medium, Colors.WHITE, Colors.BLACK,
            SCREEN_WIDTH // 2, title_y + 60, center=True
        )
        
        # Botão de iniciar
        button_width, button_height = 220, 50
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        button_y = SCREEN_HEIGHT // 2
        
        start_button = self.draw_button(">>> INICIAR JOGO <<<", button_x, button_y, button_width, button_height, True)
        
        # Instruções com símbolos ASCII
        instructions_y = SCREEN_HEIGHT // 2 + 100
        instructions = [
            "=== Como Jogar ===",
            "[WASD] ou [Setas] - Mover",
            "[ESPACO] - Colocar Bomba", 
            "* Destrua blocos e inimigos",
            "+ Colete power-ups",
            "! Seja o ultimo sobrevivente!"
        ]
        
        # Fundo das instruções com bordas arredondadas
        inst_bg = pygame.Rect(SCREEN_WIDTH // 2 - 170, instructions_y - 15, 340, len(instructions) * 25 + 30)
        pygame.draw.rect(self.screen, (0, 0, 0, 150), inst_bg)
        pygame.draw.rect(self.screen, Colors.YELLOW, inst_bg, 2)
        
        for i, instruction in enumerate(instructions):
            color = Colors.YELLOW if i == 0 else Colors.WHITE
            font = self.font_medium if i == 0 else self.font_small
            self.draw_text_with_shadow(
                instruction, font, color, Colors.BLACK,
                SCREEN_WIDTH // 2, instructions_y + i * 25, center=True
            )
        
        # Adicionar dica de áudio
        audio_tip_y = SCREEN_HEIGHT - 40
        self.draw_text_with_shadow(
            "[AUDIO] Clique no botao de som para mutar/desmutar", self.font_small, Colors.LIGHT_GRAY, Colors.BLACK,
            SCREEN_WIDTH // 2, audio_tip_y, center=True
        )
        
        return {"start_button": start_button}
    
    def draw_character_select_screen(self, selected_character, selected_index, sprite_manager):
       
        self.screen.fill((26, 26, 46))
        
        # Título
        self.draw_text_with_shadow(
            "=== ESCOLHA SEU HEROI ===", self.font_large, Colors.YELLOW, Colors.BLACK,
            SCREEN_WIDTH // 2, 80, center=True
        )
        
        
        # Layout dos personagens em grid 3x2 (3 colunas, 2 linhas)
        character_size = 100  # Reduzido para caber melhor
        spacing = 60  # Espaçamento menor
        
        # Calcular posição inicial para centralizar o grid
        total_width = 3 * character_size + 2 * spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = 120  # Um pouco mais para cima
        
        character_rects = {}
        
        for i, character in enumerate(Characters.ALL):
            row = i // 3  # 3 colunas por linha
            col = i % 3   # 3 colunas
            x = start_x + col * (character_size + spacing)
            y = start_y + row * (character_size + spacing)
            
            
            if i == selected_index:
                
                highlight_rect = pygame.Rect(x - 8, y - 8, character_size + 16, character_size + 16)
                pygame.draw.rect(self.screen, Colors.YELLOW, highlight_rect, 4)
                
                
                for j in range(3):
                    glow_rect = pygame.Rect(x - 8 - j*2, y - 8 - j*2, character_size + 16 + j*4, character_size + 16 + j*4)
                    pygame.draw.rect(self.screen, (255, 215, 0, 50), glow_rect, 2)
            
           
            char_bg = pygame.Rect(x, y, character_size, character_size)
            pygame.draw.rect(self.screen, (255, 255, 255, 25), char_bg)
            
            
            # Desenhar sprite do personagem (ajustado para o novo tamanho)
            sprite_manager.draw_sprite(self.screen, character, x + 8, y + 8, character_size - 16)
            
            
            char_name = Characters.NAMES.get(character, character)
            self.draw_text_with_shadow(
                char_name, self.font_small, Colors.WHITE, Colors.BLACK,
                x + character_size // 2, y + character_size + 25, center=True
            )
            
            character_rects[character] = char_bg
        
       
        instructions = [
            "[SETAS] Use as SETAS para navegar",
            "[ENTER] Pressione ENTER para confirmar",
            "[!] Os outros personagens serao seus inimigos!"
        ]
        
        for i, instruction in enumerate(instructions):
            self.draw_text_with_shadow(
                instruction, self.font_small, Colors.WHITE, Colors.BLACK,
                SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80 + i * 20, center=True
            )
        
        
        selected_name = Characters.NAMES.get(selected_character, selected_character)
        self.draw_text_with_shadow(
            f">>> Selecionado: {selected_name} <<<", self.font_medium, Colors.YELLOW, Colors.BLACK,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 15, center=True
        )
        
        return character_rects
    
    def draw_game_screen(self, score, lives, level, bombs):
        
        hud_height = 40
        hud_rect = pygame.Rect(0, 0, SCREEN_WIDTH, hud_height)
        pygame.draw.rect(self.screen, (0, 0, 0, 200), hud_rect)
        
        
        stats = [
            f"PONTOS: {score}",
            f"VIDAS: {lives}",
            f"NIVEL: {level}",
            f"BOMBAS: {bombs}"
        ]
        
        stat_width = SCREEN_WIDTH // len(stats)
        for i, stat in enumerate(stats):
            color = [Colors.YELLOW, Colors.RED, (78, 205, 196), Colors.ORANGE][i]
            self.draw_text_with_shadow(
                stat, self.font_small, color, Colors.BLACK,
                stat_width * i + stat_width // 2, hud_height // 2, center=True
            )
        
        
        controls_text = "[WASD/SETAS]: Mover | [ESPACO]: Bomba | [P]: Pausar"
        self.draw_text_with_shadow(
            controls_text, self.font_small, Colors.LIGHT_GRAY, Colors.BLACK,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 15, center=True
        )
    
    def draw_game_over_screen(self, final_score, final_level):
        
        dark_colors = [(44, 24, 16), (139, 0, 0)]
        self.draw_gradient_background(dark_colors)
        
        
        shake_x = math.sin(pygame.time.get_ticks() * 0.01) * 3
        self.draw_text_with_shadow(
            "💀 GAME OVER", self.font_large, Colors.RED, Colors.BLACK,
            SCREEN_WIDTH // 2 + shake_x, SCREEN_HEIGHT // 3, center=True
        )
        
        
        score_bg = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50, 300, 100)
        pygame.draw.rect(self.screen, (0, 0, 0, 128), score_bg)
        
        self.draw_text_with_shadow(
            f"Pontuação Final: {final_score}", self.font_medium, Colors.WHITE, Colors.BLACK,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20, center=True
        )
        
        self.draw_text_with_shadow(
            f"Nível Alcançado: {final_level}", self.font_medium, Colors.WHITE, Colors.BLACK,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10, center=True
        )
        
        
        button_width, button_height = 200, 40
        restart_button = self.draw_button(
            ">>> JOGAR NOVAMENTE", SCREEN_WIDTH // 2 - button_width // 2, 
            SCREEN_HEIGHT // 2 + 60, button_width, button_height, True
        )
        
        menu_button = self.draw_button(
            "<<< MENU PRINCIPAL", SCREEN_WIDTH // 2 - button_width // 2,
            SCREEN_HEIGHT // 2 + 110, button_width, button_height
        )
        
        return {"restart_button": restart_button, "menu_button": menu_button}
    
    def draw_victory_screen(self, score):
        
        victory_colors = [(240, 147, 251), (245, 87, 108)]
        self.draw_gradient_background(victory_colors)
        
        
        bounce_y = math.sin(pygame.time.get_ticks() * 0.005) * 20
        self.draw_text_with_shadow(
            "🏆 PARABÉNS!", self.font_large, Colors.YELLOW, Colors.BLACK,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + bounce_y, center=True
        )
        
        self.draw_text_with_shadow(
            "Você completou o nível!", self.font_medium, Colors.WHITE, Colors.BLACK,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 60, center=True
        )
        
        
        self.draw_text_with_shadow(
            f"Pontuação: {score}", self.font_medium, Colors.YELLOW, Colors.BLACK,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, center=True
        )
        
        
        button_width, button_height = 200, 40
        next_button = self.draw_button(
            ">>> PROXIMO NIVEL", SCREEN_WIDTH // 2 - button_width // 2,
            SCREEN_HEIGHT // 2 + 60, button_width, button_height, True
        )
        
        menu_button = self.draw_button(
            "<<< MENU PRINCIPAL", SCREEN_WIDTH // 2 - button_width // 2,
            SCREEN_HEIGHT // 2 + 110, button_width, button_height
        )
        
        return {"next_button": next_button, "menu_button": menu_button}
    
    def draw_pause_overlay(self):
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(Colors.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        
        self.draw_text_with_shadow(
            "=== PAUSADO ===", self.font_large, Colors.YELLOW, Colors.BLACK,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, center=True
        )
        
        self.draw_text_with_shadow(
            "[P] Pressione P para continuar", self.font_small, Colors.WHITE, Colors.BLACK,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, center=True
        )
    
    def draw_simple_speaker_icon(self, x, y, size, is_muted):
        """Desenha um ícone de alto-falante simples usando formas geométricas"""
        center_x = x + size // 2
        center_y = y + size // 2
        
        # Cor baseada no estado
        color = Colors.WHITE if not is_muted else Colors.RED
        
        # Base do alto-falante (retângulo)
        speaker_rect = pygame.Rect(center_x - 8, center_y - 6, 6, 12)
        pygame.draw.rect(self.screen, color, speaker_rect)
        
        # Cone do alto-falante (triângulo)
        cone_points = [
            (center_x - 2, center_y - 8),
            (center_x - 2, center_y + 8), 
            (center_x + 6, center_y + 4),
            (center_x + 6, center_y - 4)
        ]
        pygame.draw.polygon(self.screen, color, cone_points)
        
        if not is_muted:
            # Ondas sonoras (arcos)
            for i in range(3):
                radius = 8 + i * 4
                arc_rect = pygame.Rect(center_x + 6 - radius, center_y - radius, radius * 2, radius * 2)
                # Desenhar arcos usando linhas curvas
                start_angle = -0.5
                end_angle = 0.5
                pygame.draw.arc(self.screen, color, arc_rect, start_angle, end_angle, 2)
        else:
            # X para indicar mutado
            pygame.draw.line(self.screen, Colors.RED, 
                           (center_x + 8, center_y - 8), 
                           (center_x + 16, center_y + 8), 3)
            pygame.draw.line(self.screen, Colors.RED, 
                           (center_x + 8, center_y + 8), 
                           (center_x + 16, center_y - 8), 3)

    def draw_mute_button(self, is_muted):
        
        button_size = 45
        button_x = SCREEN_WIDTH - button_size - 10
        button_y = 10
        
        # Fundo do botão com efeito visual
        button_rect = pygame.Rect(button_x, button_y, button_size, button_size)
        
        # Cor de fundo baseada no estado
        bg_color = (100, 20, 20) if is_muted else (20, 100, 20)  # Vermelho escuro se mutado, verde escuro se ativo
        pygame.draw.rect(self.screen, bg_color, button_rect)
        
        # Borda com cor dinâmica
        border_color = Colors.RED if is_muted else Colors.GREEN
        pygame.draw.rect(self.screen, border_color, button_rect, 3)
        
        # Efeito de brilho
        if not is_muted:
            glow_rect = pygame.Rect(button_x - 1, button_y - 1, button_size + 2, button_size + 2)
            pygame.draw.rect(self.screen, (0, 200, 0), glow_rect, 1)
        
        # Desenhar ícone personalizado
        self.draw_simple_speaker_icon(button_x, button_y, button_size, is_muted)
        
        # Tooltip
        status_text = "MUDO" if is_muted else "SOM"
        tooltip_surface = self.font_small.render(status_text, True, Colors.WHITE)
        tooltip_rect = tooltip_surface.get_rect(center=(button_rect.centerx, button_rect.bottom + 15))
        
        # Fundo do tooltip
        tooltip_bg = pygame.Rect(tooltip_rect.x - 5, tooltip_rect.y - 2, tooltip_rect.width + 10, tooltip_rect.height + 4)
        pygame.draw.rect(self.screen, (0, 0, 0, 150), tooltip_bg)
        self.screen.blit(tooltip_surface, tooltip_rect)
        
        return button_rect


