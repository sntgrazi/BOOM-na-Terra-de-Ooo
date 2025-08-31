import sys
import os


try:
    import pygame
except ImportError:
    print("❌ Erro: pygame não está instalado!")
    print("Execute: pip install pygame numpy")
    print("Ou use o script install_and_run.bat (Windows) ou install_and_run.sh (Linux/Mac)")
    sys.exit(1)


try:
    import numpy
except ImportError:
    print("❌ Erro: numpy não está instalado!")
    print("Execute: pip install pygame numpy") 
    print("Ou use o script install_and_run.bat (Windows) ou install_and_run.sh (Linux/Mac)")
    sys.exit(1)

from game.bomberman_game import BombermanGame

def main():

    pygame.init()
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Bomberman Clone - Adventure Time Edition")

    try:
        icon_path = os.path.join("images", "Finn-frame1.png")
        if os.path.exists(icon_path):
            icon = pygame.image.load(icon_path)
            pygame.display.set_icon(icon)
    except:
        pass  

    game = BombermanGame(screen)
    game.run()
    
    # Finalizar
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
