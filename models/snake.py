from enums import Direction
from config import GRID_WIDTH, GRID_HEIGHT

class Snake:
    def __init__(self, start_pos, color, name):
        self.body = [start_pos]
        self.direction = Direction.RIGHT
        self.color = color
        self.name = name
        self.score = 0
        self.alive = True
        
    def get_head(self):
        return self.body[0]
    
    def move(self, grow=False):
        if not self.alive:
            return
            
        head_x, head_y = self.body[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)
        
        self.body.insert(0, new_head)
        
        if not grow:
            self.body.pop()
    
    def check_wall_collision(self):
        head_x, head_y = self.get_head()
        return (head_x < 0 or head_x >= GRID_WIDTH or 
                head_y < 0 or head_y >= GRID_HEIGHT)
    
    def check_self_collision(self):
        head = self.get_head()
        return head in self.body[1:]
    
    def check_collision_with_snake(self, other_snake):
        head = self.get_head()
        return head in other_snake.body