SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 50
COLS = SCREEN_WIDTH // TILE_SIZE
ROWS = SCREEN_HEIGHT // TILE_SIZE

PLAYER_SPEED = 2
ENEMY_SPEED = 1
FPS = 60

BOMB_TIMER = 3000
EXPLOSION_DURATION = 500
EXPLOSION_RANGE = 2

class GameState:
    START = "start"
    CHARACTER_SELECT = "character_select"
    PLAYING = "playing"
    GAME_OVER = "game_over"
    VICTORY = "victory"
    PAUSED = "paused"

class Characters:
    FINN = "finn"
    JAKE = "jake"
    MARCELINE = "marceline"
    PRINCESS_LUMP = "Princesa Caroço"
    FIRE_PRINCESS = "fire_princess"
    JELLYBEAN_PRINCESS = "jellybean_princess"
    
    ALL = [FINN, JAKE, MARCELINE, PRINCESS_LUMP, FIRE_PRINCESS, JELLYBEAN_PRINCESS]
    NAMES = {
        FINN: "Finn (Aventureiro)",
        JAKE: "Jake (Cachorro)",
        MARCELINE: "Marceline (Vampira)",
        PRINCESS_LUMP: "Princesa Caroço",
        FIRE_PRINCESS: "Princesa do Fogo",
        JELLYBEAN_PRINCESS: "Princesa Jujuba"
    }

class TileType:
    EMPTY = 0
    WALL = 1
    BRICK = 2
    BOMB = 3
    EXPLOSION = 4
    POWERUP_BOMB = 5
    POWERUP_RANGE = 6
    POWERUP_SPEED = 7

class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 165, 0)
    PURPLE = (128, 0, 128)
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)
    LIGHT_GRAY = (192, 192, 192)
    
    WALL_COLOR = (68, 68, 68)
    BRICK_COLOR = (205, 133, 63)
    EXPLOSION_COLOR = (255, 107, 53)
    EXPLOSION_CENTER = (255, 215, 0)
    
    POWERUP_BOMB = (78, 205, 196)
    POWERUP_RANGE = (255, 107, 53)
    POWERUP_SPEED = (150, 206, 180)
    
    UI_BACKGROUND = (0, 0, 0, 128)
    UI_TEXT = (255, 255, 255)
    UI_HIGHLIGHT = (255, 215, 0)

class Direction:
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3
    
    DELTAS = {
        UP: (0, -1),
        RIGHT: (1, 0),
        DOWN: (0, 1),
        LEFT: (-1, 0)
    }