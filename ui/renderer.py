import pygame
from config import *

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 28)
        self.big_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 22)
    
    def draw(self, game_state):
        self.screen.fill(BLACK)
        

        self._draw_grid()
        

        self._draw_snake(game_state.snake1, ORANGE, DARK_ORANGE)
        self._draw_snake(game_state.snake2, CYAN, DARK_CYAN)
        

        self._draw_food(game_state.food)
        

        self._draw_ui(game_state)
        
        pygame.display.flip()
    
    def _draw_grid(self):
        for x in range(0, WINDOW_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, UI_HEIGHT), (x, WINDOW_HEIGHT))
        for y in range(UI_HEIGHT, WINDOW_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (WINDOW_WIDTH, y))
    
    def _draw_snake(self, snake, head_color, body_color):
        if not snake.alive:
            head_color = GRAY
            body_color = (64, 64, 64)
        
        for i, segment in enumerate(snake.body):
            x, y = segment
            color = head_color if i == 0 else body_color
            pygame.draw.rect(self.screen, color, 
                           (x * GRID_SIZE, y * GRID_SIZE + UI_HEIGHT, 
                            GRID_SIZE, GRID_SIZE))
    
    def _draw_food(self, food_pos):
        food_x, food_y = food_pos
        pygame.draw.rect(self.screen, RED, 
                        (food_x * GRID_SIZE, food_y * GRID_SIZE + UI_HEIGHT, 
                         GRID_SIZE, GRID_SIZE))
    
    def _draw_ui(self, game_state):

        ui_panel = pygame.Surface((WINDOW_WIDTH, 100))
        ui_panel.set_alpha(180)
        ui_panel.fill(BLACK)
        self.screen.blit(ui_panel, (0, 0))
        

        pygame.draw.line(self.screen, WHITE, (0, 100), (WINDOW_WIDTH, 100), 2)
        

        self._draw_snake_stats(game_state.snake1, 20, ORANGE, "ORANGE", game_state.ai1_type)
        self._draw_snake_stats(game_state.snake2, WINDOW_WIDTH - 200, CYAN, "CYAN", game_state.ai2_type)
        

        self._draw_center_info(game_state)
        

        if game_state.game_over:
            self._draw_game_over(game_state)
    
    def _draw_snake_stats(self, snake, x_pos, color, title, ai_type=None):

        if ai_type:
            title_text = self.font.render(f"{title} ({ai_type})", True, color)
        else:
            title_text = self.font.render(title, True, color)
        self.screen.blit(title_text, (x_pos, 10))
        
        score_text = self.font.render(f"Score: {snake.score}", True, WHITE)
        length_text = self.small_font.render(f"Length: {len(snake.body)}", True, WHITE)
        status_color = color if snake.alive else RED
        status_text = self.small_font.render(
            f"Status: {'ALIVE' if snake.alive else 'DEAD'}", 
            True, status_color
        )
        
        self.screen.blit(score_text, (x_pos, 35))
        self.screen.blit(length_text, (x_pos, 55))
        self.screen.blit(status_text, (x_pos, 75))
    
    def _draw_center_info(self, game_state):
        center_x = WINDOW_WIDTH // 2
        
        game_title = self.font.render("AI SNAKE BATTLE", True, YELLOW)
        title_rect = game_title.get_rect(center=(center_x, 25))
        self.screen.blit(game_title, title_rect)
        
        food_info = self.small_font.render(
            f"Food at ({game_state.food[0]}, {game_state.food[1]})", 
            True, WHITE
        )
        food_rect = food_info.get_rect(center=(center_x, 50))
        self.screen.blit(food_info, food_rect)
        
        speed_info = self.small_font.render("FAST MODE", True, WHITE)
        speed_rect = speed_info.get_rect(center=(center_x, 70))
        self.screen.blit(speed_info, speed_rect)
    
    def _draw_game_over(self, game_state):

        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        

        if game_state.winner:
            winner_color = ORANGE if game_state.winner == game_state.snake1 else CYAN
            winner_text = self.big_font.render(
                f"{game_state.winner.name.upper()} WINS!", 
                True, winner_color
            )
            

            stats_lines = [
                f"Final Score: {game_state.winner.score} points",
                f"Final Length: {len(game_state.winner.body)} segments",
                f"Food Consumed: {game_state.winner.score // FOOD_SCORE} items"
            ]
        else:
            winner_text = self.big_font.render("IT'S A TIE!", True, YELLOW)
            

            stats_lines = [
                f"Orange Score: {game_state.snake1.score} | Cyan Score: {game_state.snake2.score}",
                f"Orange Length: {len(game_state.snake1.body)} | Cyan Length: {len(game_state.snake2.body)}",
                f"Total Food Consumed: {(game_state.snake1.score + game_state.snake2.score) // FOOD_SCORE} items"
            ]
        

        winner_rect = winner_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
        self.screen.blit(winner_text, winner_rect)
        

        for i, line in enumerate(stats_lines):
            stat_text = self.font.render(line, True, WHITE)
            stat_rect = stat_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30 + i * 30))
            self.screen.blit(stat_text, stat_rect)
        

        restart_text = self.font.render("Press R to Restart | Press Q to Quit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80))
        self.screen.blit(restart_text, restart_rect)
        

        performance_text = self.small_font.render("High-Speed AI Battle Mode Active", True, GRAY)
        perf_rect = performance_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 120))
        self.screen.blit(performance_text, perf_rect)