#!/usr/bin/env python3

import pygame
import os

def create_block_images():
    pygame.init()

    TILE_SIZE = 40
    wall_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
    wall_surface.fill((60, 60, 60))
    pygame.draw.rect(wall_surface, (80, 80, 80), (0, 0, TILE_SIZE, 2))
    pygame.draw.rect(wall_surface, (40, 40, 40), (0, TILE_SIZE-2, TILE_SIZE, 2))
    pygame.draw.rect(wall_surface, (80, 80, 80), (0, 0, 2, TILE_SIZE))
    pygame.draw.rect(wall_surface, (40, 40, 40), (TILE_SIZE-2, 0, 2, TILE_SIZE))
    pygame.draw.rect(wall_surface, (70, 70, 70), (5, 5, TILE_SIZE-10, TILE_SIZE-10))
    
    pygame.image.save(wall_surface, "images/bloco-estrutural.png")
    print("✅ Bloco estrutural criado: images/bloco-estrutural.png")
    brick_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
    brick_surface.fill((139, 69, 19))
    for y in range(0, TILE_SIZE, 8):
        pygame.draw.line(brick_surface, (160, 82, 45), (0, y), (TILE_SIZE, y), 1)
    for x in range(0, TILE_SIZE, 10):
        for y in range(0, TILE_SIZE, 16):
            offset = 5 if (y // 16) % 2 == 0 else 0
            pygame.draw.line(brick_surface, (160, 82, 45), 
                           (x + offset, y), (x + offset, y + 8), 1)
    pygame.draw.rect(brick_surface, (160, 82, 45), (0, 0, TILE_SIZE, 1))
    pygame.draw.rect(brick_surface, (100, 50, 10), (0, TILE_SIZE-1, TILE_SIZE, 1))
    pygame.draw.rect(brick_surface, (160, 82, 45), (0, 0, 1, TILE_SIZE))
    pygame.draw.rect(brick_surface, (100, 50, 10), (TILE_SIZE-1, 0, 1, TILE_SIZE)) 
    
    pygame.image.save(brick_surface, "images/bloco-destrutivel.png")
    print("✅ Bloco destrutível criado: images/bloco-destrutivel.png")
    pygame.quit()
    print("🎨 Imagens dos blocos criadas com sucesso!")

if __name__ == "__main__":
    if not os.path.exists("images"):
        os.makedirs("images")
    create_block_images()
