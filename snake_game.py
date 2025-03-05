import pygame
import random
import sys
import json
import os
from pygame import mixer

# Initialize Pygame and mixer
pygame.init()
mixer.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

# Game settings
DIFFICULTY_SPEEDS = {
    'Easy': 8,
    'Medium': 12,
    'Hard': 16
}

# Load or create high scores
def load_high_scores():
    if os.path.exists('high_scores.json'):
        with open('high_scores.json', 'r') as f:
            return json.load(f)
    return {'Easy': 0, 'Medium': 0, 'Hard': 0}

def save_high_score(difficulty, score):
    scores = load_high_scores()
    if score > scores[difficulty]:
        scores[difficulty] = score
        with open('high_scores.json', 'w') as f:
            json.dump(scores, f)
        return True
    return False

class Snake:
    def __init__(self, difficulty='Medium'):
        self.length = 1
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.color = GREEN
        self.score = 0
        self.difficulty = difficulty
        self.paused = False
        self.game_over = False
        
        # Load sound effects
        self.eat_sound = mixer.Sound('eat.wav')
        self.crash_sound = mixer.Sound('crash.wav')

    def get_head_position(self):
        return self.positions[0]

    def update(self):
        cur = self.get_head_position()
        x, y = self.direction
        new = ((cur[0] + x) % GRID_WIDTH, (cur[1] + y) % GRID_HEIGHT)
        if new in self.positions[3:]:
            return False
        self.positions.insert(0, new)
        if len(self.positions) > self.length:
            self.positions.pop()
        return True

    def reset(self):
        self.length = 1
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.score = 0
        self.difficulty = self.difficulty
        self.paused = False
        self.game_over = False
        
        # Load sound effects
        self.eat_sound = mixer.Sound('eat.wav')
        self.crash_sound = mixer.Sound('crash.wav')

    def render(self, surface):
        for p in self.positions:
            pygame.draw.rect(surface, self.color,
                           (p[0] * GRID_SIZE, p[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position([])

    def randomize_position(self, snake_positions):
        self.position = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
        while self.position in snake_positions:
            self.position = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))

    def render(self, surface):
        pygame.draw.rect(surface, self.color,
                        (self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def draw_menu(screen, selected_difficulty):
    screen.fill(BLACK)
    font = pygame.font.Font(None, 74)
    difficulties = list(DIFFICULTY_SPEEDS.keys())
    high_scores = load_high_scores()
    
    title = font.render('Snake Game', True, GREEN)
    screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 100))
    
    y = 250
    menu_font = pygame.font.Font(None, 36)
    for diff in difficulties:
        color = YELLOW if diff == selected_difficulty else WHITE
        text = menu_font.render(f'{diff} (High Score: {high_scores[diff]})', True, color)
        screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, y))
        y += 50
    
    instructions = menu_font.render('Press ENTER to start, Arrow keys to select difficulty', True, WHITE)
    screen.blit(instructions, (WINDOW_WIDTH//2 - instructions.get_width()//2, 450))
    
    pygame.display.update()

def main():
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Snake Game')
    
    selected_difficulty = 'Medium'
    in_menu = True
    
    while in_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    in_menu = False
                elif event.key == pygame.K_UP:
                    difficulties = list(DIFFICULTY_SPEEDS.keys())
                    current_idx = difficulties.index(selected_difficulty)
                    selected_difficulty = difficulties[(current_idx - 1) % len(difficulties)]
                elif event.key == pygame.K_DOWN:
                    difficulties = list(DIFFICULTY_SPEEDS.keys())
                    current_idx = difficulties.index(selected_difficulty)
                    selected_difficulty = difficulties[(current_idx + 1) % len(difficulties)]
        
        draw_menu(screen, selected_difficulty)
        clock.tick(DIFFICULTY_SPEEDS[selected_difficulty])
    
    snake = Snake(selected_difficulty)
    food = Food()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake.direction != (0, 1):
                    snake.direction = (0, -1)
                elif event.key == pygame.K_DOWN and snake.direction != (0, -1):
                    snake.direction = (0, 1)
                elif event.key == pygame.K_LEFT and snake.direction != (1, 0):
                    snake.direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and snake.direction != (-1, 0):
                    snake.direction = (1, 0)
        
        if snake.paused:
            font = pygame.font.Font(None, 74)
            pause_text = font.render('PAUSED', True, WHITE)
            screen.blit(pause_text, (WINDOW_WIDTH//2 - pause_text.get_width()//2, WINDOW_HEIGHT//2))
            pygame.display.update()
            continue
            
        if not snake.update():
            snake.crash_sound.play()
            snake.game_over = True
            font = pygame.font.Font(None, 74)
            game_over_text = font.render('Game Over!', True, RED)
            screen.blit(game_over_text, (WINDOW_WIDTH//2 - game_over_text.get_width()//2, WINDOW_HEIGHT//2 - 50))
            
            if save_high_score(snake.difficulty, snake.score):
                new_record_text = font.render('New High Score!', True, YELLOW)
                screen.blit(new_record_text, (WINDOW_WIDTH//2 - new_record_text.get_width()//2, WINDOW_HEIGHT//2 + 50))
            
            pygame.display.update()
            pygame.time.wait(2000)
            snake.reset()
            food.randomize_position(snake.positions)
            continue

        if snake.get_head_position() == food.position:
            snake.eat_sound.play()
            snake.length += 1
            snake.score += 1
            food.randomize_position(snake.positions)

        screen.fill(BLACK)
        snake.render(screen)
        food.render(screen)
        
        # Display score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {snake.score}', True, WHITE)
        screen.blit(score_text, (10, 10))
        
        pygame.display.update()
        clock.tick(DIFFICULTY_SPEEDS[snake.difficulty])

if __name__ == '__main__':
    main()