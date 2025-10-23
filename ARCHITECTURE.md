# Brick Addiction - Architecture Documentation

## Version Comparison

### v1.0 (Original) - Procedural Design
- Single file with 287 lines
- Global variables for all game state
- Mixed concerns (logic, rendering, input handling in one loop)
- Difficult to test individual components
- Hard to extend with new features

### v2.0 (Refactored) - Object-Oriented Design
- Well-organized class structure
- Clear separation of concerns
- Easy to test and extend
- ~550 lines (more code, but much better organized)

---

## Class Structure

### Configuration Layer
**`Config`** - Centralized constants
- All game settings in one place
- Easy to tune gameplay parameters
- No magic numbers scattered throughout code

### Entity Layer
**`Paddle`** - Player paddle
- Manages position and movement
- Handles keyboard input
- Collision detection support
- Auto-play positioning

**`Ball`** - Game ball
- Physics and movement
- Wall collision detection
- Paddle collision with deflection
- Speed management

**`Brick`** - Individual brick
- Position and color
- Rendering

**`BrickManager`** - Brick collection
- Grid generation
- Collision detection with ball
- Difficulty progression
- Multi-brick rendering

### Game State Layer
**`GameState`** - Score, lives, win/lose
- Score management
- Life tracking
- Victory/game over conditions
- Board clear bonuses

**`AutoPlay`** - AI controller
- Toggle AI on/off
- Smart paddle positioning
- Deflection calculation
- Target brick selection

**`GameLogger`** - Statistics tracking
- Game duration logging
- Score persistence
- Auto-play tracking

### Coordination Layer
**`Game`** - Main coordinator
- Manages all subsystems
- Main game loop
- Event handling
- Rendering coordination
- Game reset logic

---

## Key Improvements

### 1. Separation of Concerns
**Before:**
```python
# Everything mixed together
while running:
    # Input handling
    for event in pygame.event.get():
        ...
    # Game logic
    ball_x += ball_speed_x
    # Collision detection
    if ball_rect.colliderect(brick):
        ...
    # Rendering
    pygame.draw.circle(...)
```

**After:**
```python
# Clean separation
def run(self):
    while self.running:
        self.handle_events()  # Input
        self.update()         # Logic
        self.draw()           # Rendering
```

### 2. Encapsulation
**Before:**
```python
# Global variables everywhere
paddle_x = 100
paddle_y = 200
paddle_speed = 5
```

**After:**
```python
# Data and behavior together
class Paddle:
    def __init__(self):
        self.x = 100
        self.y = 200
        self.speed = 5

    def update(self, keys):
        # Paddle-specific logic
```

### 3. Testability
**Before:**
- Can't test individual components
- Must run entire game to test features

**After:**
```python
# Can test components in isolation
paddle = Paddle(800, 600)
paddle.update(keys)
assert paddle.x == expected_x
```

### 4. Extensibility
**Before:**
- Adding features requires modifying the main loop
- Global state makes changes risky

**After:**
- Add new entity by creating a class
- Extend behavior through inheritance
- Add features without touching existing code

---

## Design Patterns Used

### 1. Single Responsibility Principle
Each class has one clear purpose:
- `Paddle` only handles paddle behavior
- `Ball` only handles ball physics
- `GameState` only tracks game state

### 2. Dependency Injection
```python
game = Game(auto_play=False)  # Configuration injected
```

### 3. Manager Pattern
```python
BrickManager  # Manages collection of bricks
GameState     # Manages game state
```

### 4. Static Factory Method
```python
GameLogger.log_game(...)  # Utility without instance state
```

---

## Future Extension Examples

### Adding Power-ups
```python
class PowerUp:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type  # 'multiball', 'grow', 'slow'

    def apply(self, game):
        # Apply effect to game

class PowerUpManager:
    def spawn_random(self, x, y):
        # Create power-up at brick location
```

### Adding Particle Effects
```python
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.lifetime = 30

class ParticleSystem:
    def emit(self, x, y, count):
        # Create particles at location
```

### Adding Sound Effects
```python
class SoundManager:
    def __init__(self):
        self.sounds = {
            'hit': pygame.mixer.Sound('hit.wav'),
            'break': pygame.mixer.Sound('break.wav')
        }

    def play(self, sound_name):
        self.sounds[sound_name].play()
```

---

## Benefits Summary

### Maintainability
- Find code faster (know which class to look in)
- Change code safely (isolated components)
- Understand code easier (clear structure)

### Testability
- Unit test individual classes
- Mock dependencies for testing
- Verify behavior in isolation

### Extensibility
- Add features without breaking existing code
- Reuse components in different contexts
- Override behavior through inheritance

### Readability
- Self-documenting structure
- Clear responsibilities
- Logical organization

---

## Migration Notes

All features from v1.0 are preserved in v2.0:
- Auto-play mode
- Dynamic difficulty
- Progressive scoring
- Lives system
- Victory condition (18 rows)
- Game statistics logging
- Ball speed acceleration
- Deflection physics

The refactored version is a drop-in replacement with identical gameplay.
