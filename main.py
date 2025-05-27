import pygame
import sys
from config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from game.game_state import GameState
from ui.renderer import Renderer
from ui.menu import AISelectionMenu

class SnakeGame:
    def __init__(self):

        pygame.init()
        

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("AI Snake Battle")
        

        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.screen)
        

        menu = AISelectionMenu(self.screen)
        ai_selection = menu.run()
        
        if ai_selection:
            ai1_type, ai2_type = ai_selection
            self.game_state = GameState(ai1_type, ai2_type)
        else:

            pygame.quit()
            sys.exit()
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False
                elif event.key == pygame.K_r:

                    menu = AISelectionMenu(self.screen)
                    ai_selection = menu.run()
                    
                    if ai_selection:
                        ai1_type, ai2_type = ai_selection
                        self.game_state = GameState(ai1_type, ai2_type)
                    else:
                        return False
        return True
    
    def run(self):
        running = True
        
        while running:

            running = self.handle_events()
            

            self.game_state.update()
            

            self.renderer.draw(self.game_state)
            

            self.clock.tick(FPS)
        

        pygame.quit()
        sys.exit()

def main():
    game = SnakeGame()
    game.run()

if __name__ == "__main__":
    print("Welcome to AI Snake Battle!")
    main()