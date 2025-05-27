import random
from models.snake import Snake
from game.ai_controller import AIController
from game.ai_strategies import BalancedAI, AggressiveAI, DefensiveAI
from enums import Direction
from config import (
    GRID_WIDTH, GRID_HEIGHT, ORANGE, CYAN, FOOD_SCORE
)

class GameState:
    def __init__(self, ai1_type="Balanced", ai2_type="Balanced"):
        self.ai1_type = ai1_type
        self.ai2_type = ai2_type
        self.reset()
        
    def reset(self):

        self.snake1 = Snake((5, GRID_HEIGHT // 2), ORANGE, "Orange Snake")
        self.snake2 = Snake((GRID_WIDTH - 6, GRID_HEIGHT // 2), CYAN, "Cyan Snake")
        self.snake2.direction = Direction.LEFT
        

        ai_classes = {
            "Balanced": BalancedAI,
            "Aggressive": AggressiveAI,
            "Defensive": DefensiveAI
        }
        

        self.ai1_controller = ai_classes[self.ai1_type](self.snake1, self.snake2)
        self.ai2_controller = ai_classes[self.ai2_type](self.snake1, self.snake2)
        
        self.food = self.generate_food()
        self.game_over = False
        self.winner = None
    
    def generate_food(self):
        while True:
            food = (random.randint(0, GRID_WIDTH - 1), 
                   random.randint(0, GRID_HEIGHT - 1))
            if (food not in self.snake1.body and 
                food not in self.snake2.body):
                return food
    
    def update(self):
        if self.game_over:
            return
        

        if self.snake1.alive:
            self.ai1_controller.make_decision(self.snake1, self.food)
        if self.snake2.alive:
            self.ai2_controller.make_decision(self.snake2, self.food)
        

        food_eaten_by = None
        
        if self.snake1.alive:

            head_x, head_y = self.snake1.get_head()
            dx, dy = self.snake1.direction.value
            next_pos = (head_x + dx, head_y + dy)
            
            will_eat_food = (next_pos == self.food)
            self.snake1.move(grow=will_eat_food)
            
            if will_eat_food:
                food_eaten_by = self.snake1
        
        if self.snake2.alive:

            head_x, head_y = self.snake2.get_head()
            dx, dy = self.snake2.direction.value
            next_pos = (head_x + dx, head_y + dy)
            
            will_eat_food = (next_pos == self.food) and food_eaten_by is None
            self.snake2.move(grow=will_eat_food)
            
            if will_eat_food:
                food_eaten_by = self.snake2
        

        if food_eaten_by:
            food_eaten_by.score += FOOD_SCORE
            self.food = self.generate_food()
        

        self._check_collisions()
        

        self._check_win_condition()
    
    def _check_collisions(self):

        if self.snake1.alive and self.snake1.check_wall_collision():
            self.snake1.alive = False
        
        if self.snake2.alive and self.snake2.check_wall_collision():
            self.snake2.alive = False
        

        if self.snake1.alive and self.snake1.check_self_collision():
            self.snake1.alive = False
        
        if self.snake2.alive and self.snake2.check_self_collision():
            self.snake2.alive = False
        

        if (self.snake1.alive and self.snake2.alive):
            snake1_head = self.snake1.get_head()
            snake2_head = self.snake2.get_head()
            

            if snake1_head == snake2_head:

                self.snake1.alive = False
                self.snake2.alive = False
            else:

                if self.snake1.check_collision_with_snake(self.snake2):
                    self.snake1.alive = False
                
                if self.snake2.check_collision_with_snake(self.snake1):
                    self.snake2.alive = False
    
    def _check_win_condition(self):
        if not self.snake1.alive and not self.snake2.alive:
            self.game_over = True

            if self.snake1.score > self.snake2.score:
                self.winner = self.snake1
            elif self.snake2.score > self.snake1.score:
                self.winner = self.snake2
            else:
                self.winner = None
        elif not self.snake1.alive:
            self.game_over = True
            self.winner = self.snake2
        elif not self.snake2.alive:
            self.game_over = True
            self.winner = self.snake1