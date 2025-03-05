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
PURPLE = (128, 0, 128)

# Game settings
DIFFICULTY_SPEEDS = {
    'Easy': 8,
    'Medium': 12,
    'Hard': 16
}

# Power-up types
POWER_UP_TYPES = {
    'speed': {'color': BLUE, 'duration': 5000},  # 5 seconds
    'invincible': {'color': YELLOW, 'duration': 3000},  # 3 seconds
    'double_points': {'color': PURPLE, 'duration': 7000}  # 7 seconds
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

class PowerUp:
    def __init__(self):
        self.active = False
        self.position = (0, 0)
        self.type = None
        self.spawn_time = 0
        self.duration = 0

    def spawn(self, snake_positions):
        self.type = random.choice(list(POWER_UP_TYPES.keys()))
        self.position = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
        while self.position in snake_positions:
            self.position = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
        self.active = True
        self.spawn_time = pygame.time.get_ticks()
        self.duration = POWER_UP_TYPES[self.type]['duration']

    def render(self, surface):
        if self.active and self.type is not None:
            pygame.draw.rect(surface, POWER_UP_TYPES[self.type]['color'],
                           (self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

class Obstacle:
    def __init__(self):
        self.positions = []
        self.color = WHITE

    def generate(self, snake_positions):
        self.positions = []
        num_obstacles = random.randint(3, 7)
        for _ in range(num_obstacles):
            pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
            while pos in snake_positions or pos in self.positions:
                pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
            self.positions.append(pos)

    def render(self, surface):
        for pos in self.positions:
            pygame.draw.rect(surface, self.color,
                           (pos[0] * GRID_SIZE, pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

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
        self.power_ups = {}
        self.invincible = False
        self.speed_multiplier = 1
        self.point_multiplier = 1
        
        # Load sound effects
        self.eat_sound = mixer.Sound('eat.wav')
        self.crash_sound = mixer.Sound('crash.wav')

    def get_head_position(self):
        return self.positions[0]

    def update(self, obstacles):
        cur = self.get_head_position()
        x, y = self.direction
        new = ((cur[0] + x) % GRID_WIDTH, (cur[1] + y) % GRID_HEIGHT)

        # Check collision with obstacles
        if not self.invincible and new in obstacles.positions:
            return False

        # Check collision with self
        if not self.invincible and new in self.positions[3:]:
            return False

        self.positions.insert(0, new)
        if len(self.positions) > self.length:
            self.positions.pop()

        # Update power-ups
        current_time = pygame.time.get_ticks()
        for power_up_type in list(self.power_ups.keys()):
            if current_time - self.power_ups[power_up_type] >= POWER_UP_TYPES[power_up_type]['duration']:
                self._remove_power_up(power_up_type)

        return True

    def apply_power_up(self, power_up_type):
        self.power_ups[power_up_type] = pygame.time.get_ticks()
        if power_up_type == 'speed':
            self.speed_multiplier = 1.5
        elif power_up_type == 'invincible':
            self.invincible = True
            self.color = YELLOW
        elif power_up_type == 'double_points':
            self.point_multiplier = 2

    def _remove_power_up(self, power_up_type):
        if power_up_type in self.power_ups:
            del self.power_ups[power_up_type]
            if power_up_type == 'speed':
                self.speed_multiplier = 1
            elif power_up_type == 'invincible':
                self.invincible = False
                self.color = GREEN
            elif power_up_type == 'double_points':
                self.point_multiplier = 1

    def reset(self):
        self.length = 1
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.score = 0
        self.difficulty = self.difficulty
        self.paused = False
        self.game_over = False
        self.power_ups = {}
        self.invincible = False
        self.speed_multiplier = 1
        self.point_multiplier = 1
        
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
    power_up = PowerUp()
    obstacles = Obstacle()
    obstacles.generate(snake.positions)
    
    last_power_up_time = pygame.time.get_ticks()
    power_up_interval = 10000  # 10 seconds
    
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
                elif event.key == pygame.K_p:
                    snake.paused = not snake.paused
        
        if snake.paused:
            font = pygame.font.Font(None, 74)
            pause_text = font.render('PAUSED', True, WHITE)
            screen.blit(pause_text, (WINDOW_WIDTH//2 - pause_text.get_width()//2, WINDOW_HEIGHT//2))
            pygame.display.update()
            continue
            
        if not snake.update(obstacles):
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
            obstacles.generate(snake.positions)
            continue

        # Handle power-up spawning
        current_time = pygame.time.get_ticks()
        if not power_up.active and current_time - last_power_up_time >= power_up_interval:
            power_up.spawn(snake.positions)
            last_power_up_time = current_time

        # Check for power-up collection
        if power_up.active and snake.get_head_position() == power_up.position:
            snake.apply_power_up(power_up.type)
            power_up.active = False

        if snake.get_head_position() == food.position:
            snake.eat_sound.play()
            snake.length += 1
            snake.score += 1 * snake.point_multiplier
            food.randomize_position(snake.positions)

        screen.fill(BLACK)
        snake.render(screen)
        food.render(screen)
        obstacles.render(screen)
        if power_up.active:
            power_up.render(screen)
        
        # Display score and active power-ups
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {snake.score}', True, WHITE)
        screen.blit(score_text, (10, 10))
        
        y = 50
        for power_up_type in snake.power_ups:
            power_up_text = font.render(f'{power_up_type.title()} active!', True, POWER_UP_TYPES[power_up_type]['color'])
            screen.blit(power_up_text, (10, y))
            y += 30
        
        pygame.display.update()
        clock.tick(DIFFICULTY_SPEEDS[snake.difficulty] * snake.speed_multiplier)

if __name__ == '__main__':
    main()