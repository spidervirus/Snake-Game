# Snake Game

A modern implementation of the classic Snake game with exciting power-ups, multiple difficulty levels, and high score tracking.

## Features

### Core Gameplay
- Classic snake movement and growth mechanics
- Grid-based gameplay on an 800x600 window
- Collision detection with walls, obstacles, and self
- Score tracking system

### Difficulty Levels
- Easy: Perfect for beginners
- Medium: Balanced gameplay experience
- Hard: Challenge yourself with faster snake movement

### Power-Up System
- **Speed Boost** (Blue): Increases snake movement speed for 5 seconds
- **Invincibility** (Yellow): Prevents collisions for 3 seconds
- **Double Points** (Purple): Doubles score gains for 7 seconds

### Additional Features
- High score tracking for each difficulty level
- Persistent high scores saved between sessions
- Pause functionality
- Sound effects for eating and crashing
- Random obstacle generation
- Visual indicators for active power-ups

## Controls

- **Arrow Keys**: Control snake direction
- **P**: Pause/Resume game
- **Enter**: Start game
- **Up/Down Arrows** (in menu): Select difficulty level

## Installation

1. Ensure you have Python installed on your system
2. Install the required dependencies:
   ```bash
   pip install pygame
   ```
3. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/Snake-Game.git
   ```
4. Navigate to the game directory and run:
   ```bash
   python snake_game.py
   ```

## Game Elements

- **Snake**: Green (Yellow when invincible)
- **Food**: Red
- **Obstacles**: White
- **Power-ups**:
  - Blue: Speed boost
  - Yellow: Invincibility
  - Purple: Double points

## Technical Details

- Built with Python and Pygame
- Object-oriented design with separate classes for Snake, Food, Obstacles, and Power-ups
- Configurable game settings through constants
- JSON-based high score persistence

## Contributing

Feel free to fork this repository and submit pull requests with your improvements!

## License

This project is open source and available under the MIT License.