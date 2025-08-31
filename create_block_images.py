#!/usr/bin/env python3
"""
Script para criar imagens de exemplo dos blocos estruturais e destrutíveis
"""

import pygame
import os

def create_block_images():
    """Cria imagens de exemplo para os blocos"""
    
    # Inicializar pygame
    pygame.init()
    
    # Tamanho do tile
    TILE_SIZE = 40
    
    # 🧱 CRIAR BLOCO ESTRUTURAL (indestrutível) - Cinza escuro com bordas
    wall_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
    wall_surface.fill((60, 60, 60))  # Cinza escuro
    
    # Bordas do bloco estrutural
    pygame.draw.rect(wall_surface, (80, 80, 80), (0, 0, TILE_SIZE, 2))  # Topo
    pygame.draw.rect(wall_surface, (40, 40, 40), (0, TILE_SIZE-2, TILE_SIZE, 2))  # Base
    pygame.draw.rect(wall_surface, (80, 80, 80), (0, 0, 2, TILE_SIZE))  # Esquerda
    pygame.draw.rect(wall_surface, (40, 40, 40), (TILE_SIZE-2, 0, 2, TILE_SIZE))  # Direita
    
    # Detalhes no bloco estrutural
    pygame.draw.rect(wall_surface, (70, 70, 70), (5, 5, TILE_SIZE-10, TILE_SIZE-10))
    
    # Salvar bloco estrutural
    pygame.image.save(wall_surface, "images/bloco-estrutural.png")
    print("✅ Bloco estrutural criado: images/bloco-estrutural.png")
    
    # 🧱 CRIAR BLOCO DESTRUTÍVEL - Marrom com textura de tijolo
    brick_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
    brick_surface.fill((139, 69, 19))  # Marrom tijolo
    
    # Textura de tijolo
    # Linhas horizontais
    for y in range(0, TILE_SIZE, 8):
        pygame.draw.line(brick_surface, (160, 82, 45), (0, y), (TILE_SIZE, y), 1)
    
    # Linhas verticais alternadas
    for x in range(0, TILE_SIZE, 10):
        for y in range(0, TILE_SIZE, 16):
            offset = 5 if (y // 16) % 2 == 0 else 0
            pygame.draw.line(brick_surface, (160, 82, 45), 
                           (x + offset, y), (x + offset, y + 8), 1)
    
    # Bordas do bloco destrutível
    pygame.draw.rect(brick_surface, (160, 82, 45), (0, 0, TILE_SIZE, 1))  # Topo
    pygame.draw.rect(brick_surface, (100, 50, 10), (0, TILE_SIZE-1, TILE_SIZE, 1))  # Base
    pygame.draw.rect(brick_surface, (160, 82, 45), (0, 0, 1, TILE_SIZE))  # Esquerda
    pygame.draw.rect(brick_surface, (100, 50, 10), (TILE_SIZE-1, 0, 1, TILE_SIZE))  # Direita
    
    # Salvar bloco destrutível
    pygame.image.save(brick_surface, "images/bloco-destrutivel.png")
    print("✅ Bloco destrutível criado: images/bloco-destrutivel.png")
    
    pygame.quit()
    print("🎨 Imagens dos blocos criadas com sucesso!")

if __name__ == "__main__":
    # Criar pasta images se não existir
    if not os.path.exists("images"):
        os.makedirs("images")
    
    create_block_images()
