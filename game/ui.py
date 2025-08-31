"""
Sistema de interface do usuário para o Bomberman
Menus, HUD e telas do jogo
"""

import pygame
import math
from .constants import *

class UI:
    def __init__(self, screen):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Cores dos gradientes
        self.gradient_colors = [
            (255, 107, 107),  # Vermelho
            (78, 205, 196),   # Azul-verde
            (69, 183, 209),   # Azul
            (150, 206, 180)   # Verde
        ]
        self.gradient_offset = 0
    
    def update(self, dt):
        """Atualiza animações da UI"""
        self.gradient_offset += dt * 0.001  # Velocidade do gradiente
    
    def draw_gradient_background(self, colors=None):
        """Desenha um fundo com gradiente animado"""
        if colors is None:
            colors = self.gradient_colors
        
        # Criar gradiente vertical animado
        for y in range(SCREEN_HEIGHT):
            # Calcular cor baseada na posição e tempo
            progress = (y / SCREEN_HEIGHT + self.gradient_offset) % 1.0
            color_index = int(progress * len(colors))
            next_color_index = (color_index + 1) % len(colors)
            
            # Interpolar entre cores
            blend = (progress * len(colors)) % 1.0
            color1 = colors[color_index]
            color2 = colors[next_color_index]
            
            r = int(color1[0] * (1 - blend) + color2[0] * blend)
            g = int(color1[1] * (1 - blend) + color2[1] * blend)
            b = int(color1[2] * (1 - blend) + color2[2] * blend)
            
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    
    def draw_text_with_shadow(self, text, font, color, shadow_color, x, y, center=False):
        """Desenha texto com sombra"""
        # Sombra
        shadow_surface = font.render(text, True, shadow_color)
        shadow_rect = shadow_surface.get_rect()
        if center:
            shadow_rect.center = (x + 2, y + 2)
        else:
            shadow_rect.topleft = (x + 2, y + 2)
        self.screen.blit(shadow_surface, shadow_rect)
        
        # Texto principal
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)
        
        return text_rect
    
    def draw_button(self, text, x, y, width, height, active=False):
        """Desenha um botão"""
        # Cor do botão
        if active:
            button_color = (255, 69, 0)  # Laranja avermelhado
            text_color = Colors.WHITE
        else:
            button_color = (255, 71, 87)  # Vermelho
            text_color = Colors.WHITE
        
        # Desenhar botão
        button_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, button_color, button_rect)
        pygame.draw.rect(self.screen, Colors.BLACK, button_rect, 3)
        
        # Efeito de brilho se ativo
        if active:
            pygame.draw.rect(self.screen, (255, 255, 255, 100), button_rect, 2)
        
        # Texto do botão
        text_rect = self.draw_text_with_shadow(
            text, self.font_medium, text_color, Colors.BLACK,
            x + width // 2, y + height // 2, center=True
        )
        
        return button_rect
    
    def draw_start_screen(self):
        """Desenha a tela inicial"""
        self.draw_gradient_background()
        
        # Título principal
        title_y = SCREEN_HEIGHT // 4
        self.draw_text_with_shadow(
            "💣 BOMBERMAN", self.font_large, Colors.YELLOW, Colors.BLACK,
            SCREEN_WIDTH // 2, title_y, center=True
        )
        
        # Subtítulo
        self.draw_text_with_shadow(
            "Clone", self.font_medium, Colors.WHITE, Colors.BLACK,
            SCREEN_WIDTH // 2, title_y + 60, center=True
        )
        
        # Botão iniciar
        button_width, button_height = 200, 50
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        button_y = SCREEN_HEIGHT // 2
        
        start_button = self.draw_button("INICIAR JOGO", button_x, button_y, button_width, button_height, True)
        
        # Instruções
        instructions_y = SCREEN_HEIGHT // 2 + 100
        instructions = [
            "Como Jogar:",
            "🎮 WASD ou Setas - Mover",
            "💣 ESPAÇO - Colocar Bomba", 
            "🎯 Destrua blocos e inimigos",
            "⭐ Colete power-ups"
        ]
        
        # Fundo das instruções
        inst_bg = pygame.Rect(SCREEN_WIDTH // 2 - 150, instructions_y - 10, 300, len(instructions) * 25 + 20)
        pygame.draw.rect(self.screen, (0, 0, 0, 128), inst_bg)
        
        for i, instruction in enumerate(instructions):
            color = Colors.YELLOW if i == 0 else Colors.WHITE
            font = self.font_medium if i == 0 else self.font_small
            self.draw_text_with_shadow(
                instruction, font, color, Colors.BLACK,
                SCREEN_WIDTH // 2, instructions_y + i * 25, center=True
            )
        
        return {"start_button": start_button}
    
    def draw_character_select_screen(self, selected_character, selected_index, sprite_manager):
        """Desenha a tela de seleção de personagem"""
        # Fundo escuro
        self.screen.fill((26, 26, 46))
        
        # Título
        self.draw_text_with_shadow(
            "ESCOLHA SEU PERSONAGEM", self.font_large, Colors.YELLOW, Colors.BLACK,
            SCREEN_WIDTH // 2, 80, center=True
        )
        
        # Grid de personagens 2x2
        character_size = 120
        spacing = 80
        start_x = SCREEN_WIDTH // 2 - character_size - spacing // 2
        start_y = 140
        
        character_rects = {}
        
        for i, character in enumerate(Characters.ALL):
            row = i // 2
            col = i % 2
            x = start_x + col * (character_size + spacing)
            y = start_y + row * (character_size + spacing)
            
            # Destacar personagem selecionado
            if i == selected_index:
                # Borda dourada
                highlight_rect = pygame.Rect(x - 8, y - 8, character_size + 16, character_size + 16)
                pygame.draw.rect(self.screen, Colors.YELLOW, highlight_rect, 4)
                
                # Efeito de brilho
                for j in range(3):
                    glow_rect = pygame.Rect(x - 8 - j*2, y - 8 - j*2, character_size + 16 + j*4, character_size + 16 + j*4)
                    pygame.draw.rect(self.screen, (255, 215, 0, 50), glow_rect, 2)
            
            # Fundo do personagem
            char_bg = pygame.Rect(x, y, character_size, character_size)
            pygame.draw.rect(self.screen, (255, 255, 255, 25), char_bg)
            
            # Desenhar personagem
            sprite_manager.draw_sprite(self.screen, character, x + 10, y + 10, character_size - 20)
            
            # Nome do personagem
            char_name = Characters.NAMES.get(character, character)
            self.draw_text_with_shadow(
                char_name, self.font_small, Colors.WHITE, Colors.BLACK,
                x + character_size // 2, y + character_size + 25, center=True
            )
            
            character_rects[character] = char_bg
        
        # Instruções
        instructions = [
            "Use as SETAS para navegar",
            "Pressione ENTER para confirmar",
            "Os outros personagens serão seus inimigos!"
        ]
        
        for i, instruction in enumerate(instructions):
            self.draw_text_with_shadow(
                instruction, self.font_small, Colors.WHITE, Colors.BLACK,
                SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80 + i * 20, center=True
            )
        
        # Personagem selecionado em destaque
        selected_name = Characters.NAMES.get(selected_character, selected_character)
        self.draw_text_with_shadow(
            f"Selecionado: {selected_name}", self.font_medium, Colors.YELLOW, Colors.BLACK,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 15, center=True
        )
        
        return character_rects
    
    def draw_game_screen(self, score, lives, level, bombs):
        """Desenha a tela de jogo (apenas o HUD)"""
        # HUD superior
        hud_height = 40
        hud_rect = pygame.Rect(0, 0, SCREEN_WIDTH, hud_height)
        pygame.draw.rect(self.screen, (0, 0, 0, 200), hud_rect)
        
        # Estatísticas
        stats = [
            f"Pontuação: {score}",
            f"Vidas: {lives}",
            f"Nível: {level}",
            f"Bombas: {bombs}"
        ]
        
        stat_width = SCREEN_WIDTH // len(stats)
        for i, stat in enumerate(stats):
            color = [Colors.YELLOW, Colors.RED, (78, 205, 196), Colors.ORANGE][i]
            self.draw_text_with_shadow(
                stat, self.font_small, color, Colors.BLACK,
                stat_width * i + stat_width // 2, hud_height // 2, center=True
            )
        
        # Controles na parte inferior
        controls_text = "WASD ou Setas: Mover | ESPAÇO: Bomba | P: Pausar"
        self.draw_text_with_shadow(
            controls_text, self.font_small, Colors.LIGHT_GRAY, Colors.BLACK,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 15, center=True
        )
    
    def draw_game_over_screen(self, final_score, final_level):
        """Desenha a tela de game over"""
        # Fundo escuro com gradiente vermelho
        dark_colors = [(44, 24, 16), (139, 0, 0)]
        self.draw_gradient_background(dark_colors)
        
        # Título com animação de tremor
        shake_x = math.sin(pygame.time.get_ticks() * 0.01) * 3
        self.draw_text_with_shadow(
            "💀 GAME OVER", self.font_large, Colors.RED, Colors.BLACK,
            SCREEN_WIDTH // 2 + shake_x, SCREEN_HEIGHT // 3, center=True
        )
        
        # Pontuação final
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
        
        # Botões
        button_width, button_height = 180, 40
        restart_button = self.draw_button(
            "JOGAR NOVAMENTE", SCREEN_WIDTH // 2 - button_width // 2, 
            SCREEN_HEIGHT // 2 + 60, button_width, button_height, True
        )
        
        menu_button = self.draw_button(
            "MENU PRINCIPAL", SCREEN_WIDTH // 2 - button_width // 2,
            SCREEN_HEIGHT // 2 + 110, button_width, button_height
        )
        
        return {"restart_button": restart_button, "menu_button": menu_button}
    
    def draw_victory_screen(self, score):
        """Desenha a tela de vitória"""
        # Fundo colorido
        victory_colors = [(240, 147, 251), (245, 87, 108)]
        self.draw_gradient_background(victory_colors)
        
        # Título com animação de pulo
        bounce_y = math.sin(pygame.time.get_ticks() * 0.005) * 20
        self.draw_text_with_shadow(
            "🏆 PARABÉNS!", self.font_large, Colors.YELLOW, Colors.BLACK,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + bounce_y, center=True
        )
        
        self.draw_text_with_shadow(
            "Você completou o nível!", self.font_medium, Colors.WHITE, Colors.BLACK,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 60, center=True
        )
        
        # Pontuação
        self.draw_text_with_shadow(
            f"Pontuação: {score}", self.font_medium, Colors.YELLOW, Colors.BLACK,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, center=True
        )
        
        # Botões
        button_width, button_height = 180, 40
        next_button = self.draw_button(
            "PRÓXIMO NÍVEL", SCREEN_WIDTH // 2 - button_width // 2,
            SCREEN_HEIGHT // 2 + 60, button_width, button_height, True
        )
        
        menu_button = self.draw_button(
            "MENU PRINCIPAL", SCREEN_WIDTH // 2 - button_width // 2,
            SCREEN_HEIGHT // 2 + 110, button_width, button_height
        )
        
        return {"next_button": next_button, "menu_button": menu_button}
    
    def draw_pause_overlay(self):
        """Desenha overlay de pausa"""
        # Overlay semi-transparente
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(Colors.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Texto de pausa
        self.draw_text_with_shadow(
            "PAUSADO", self.font_large, Colors.YELLOW, Colors.BLACK,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, center=True
        )
        
        self.draw_text_with_shadow(
            "Pressione P para continuar", self.font_small, Colors.WHITE, Colors.BLACK,
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, center=True
        )
    
    def draw_mute_button(self, is_muted):
        """Desenha o botão de mudo"""
        button_size = 40
        button_x = SCREEN_WIDTH - button_size - 10
        button_y = 10
        
        # Botão
        button_rect = pygame.Rect(button_x, button_y, button_size, button_size)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), button_rect)
        pygame.draw.rect(self.screen, Colors.WHITE, button_rect, 2)
        
        # Ícone
        icon = "🔇" if is_muted else "🔊"
        icon_surface = self.font_medium.render(icon, True, Colors.WHITE)
        icon_rect = icon_surface.get_rect(center=button_rect.center)
        self.screen.blit(icon_surface, icon_rect)
        
        return button_rect


