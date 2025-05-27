import pygame
from config import *

class AISelectionMenu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)
        

        self.ai_options = ["Balanced", "Aggressive", "Defensive"]
        self.ai_descriptions = {
            "Balanced": "Equal focus on food and survival",
            "Aggressive": "Prioritizes blocking opponent and taking risks",
            "Defensive": "Prioritizes survival and avoiding risks"
        }
        

        self.snake1_selection = 0  # Index in ai_options
        self.snake2_selection = 0
        self.current_snake = 1  # 1 or 2
        self.selection_complete = False
        
    def draw(self):
        self.screen.fill(BLACK)
        

        title = self.title_font.render("AI SNAKE BATTLE", True, YELLOW)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        

        subtitle = self.font.render("Select AI Behavior", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(subtitle, subtitle_rect)
        

        snake_color = ORANGE if self.current_snake == 1 else CYAN
        snake_name = "ORANGE SNAKE" if self.current_snake == 1 else "CYAN SNAKE"
        current_selection = self.snake1_selection if self.current_snake == 1 else self.snake2_selection
        
        snake_text = self.font.render(f"Selecting for {snake_name}", True, snake_color)
        snake_rect = snake_text.get_rect(center=(WINDOW_WIDTH // 2, 180))
        self.screen.blit(snake_text, snake_rect)
        

        y_start = 250
        for i, option in enumerate(self.ai_options):
            y = y_start + i * 100
            
            # Highlight selected option
            if i == current_selection:

                pygame.draw.rect(self.screen, snake_color, 
                               (WINDOW_WIDTH // 2 - 250, y - 30, 500, 80), 3)
            

            option_text = self.font.render(option, True, WHITE)
            option_rect = option_text.get_rect(center=(WINDOW_WIDTH // 2, y))
            self.screen.blit(option_text, option_rect)
            

            desc_text = self.small_font.render(self.ai_descriptions[option], True, GRAY)
            desc_rect = desc_text.get_rect(center=(WINDOW_WIDTH // 2, y + 25))
            self.screen.blit(desc_text, desc_rect)
        

        instructions = [
            "↑↓ Arrow Keys: Select AI",
            "ENTER: Confirm Selection",
            "ESC: Quit"
        ]
        
        y = WINDOW_HEIGHT - 120
        for instruction in instructions:
            inst_text = self.small_font.render(instruction, True, WHITE)
            inst_rect = inst_text.get_rect(center=(WINDOW_WIDTH // 2, y))
            self.screen.blit(inst_text, inst_rect)
            y += 30
        

        if self.current_snake == 2:
            selection_text = self.small_font.render(
                f"Orange: {self.ai_options[self.snake1_selection]}", 
                True, ORANGE
            )
            selection_rect = selection_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 20))
            self.screen.blit(selection_text, selection_rect)
        
        pygame.display.flip()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                elif event.key == pygame.K_UP:
                    if self.current_snake == 1:
                        self.snake1_selection = (self.snake1_selection - 1) % len(self.ai_options)
                    else:
                        self.snake2_selection = (self.snake2_selection - 1) % len(self.ai_options)
                
                elif event.key == pygame.K_DOWN:
                    if self.current_snake == 1:
                        self.snake1_selection = (self.snake1_selection + 1) % len(self.ai_options)
                    else:
                        self.snake2_selection = (self.snake2_selection + 1) % len(self.ai_options)
                
                elif event.key == pygame.K_RETURN:
                    if self.current_snake == 1:
                        self.current_snake = 2
                    else:
                        self.selection_complete = True
                        return True
        
        return True
    
    def run(self):
        """Run the menu and return selected AI types"""
        running = True
        
        while running and not self.selection_complete:
            running = self.handle_events()
            self.draw()
            self.clock.tick(30)
        
        if self.selection_complete:
            return (self.ai_options[self.snake1_selection], 
                    self.ai_options[self.snake2_selection])
        else:
            return None