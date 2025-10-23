# Python v3.11.5
# Brick Addiction v2.0 - Refactored with OOP Architecture

import pygame
import sys
import random
import datetime
import os
import time
from typing import List, Tuple, Optional


# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Centralized configuration for game settings"""

    # Display settings
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    FPS = 60

    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    COLORS = [
        (255, 0, 0),      # Red
        (255, 165, 0),    # Orange
        (255, 255, 0),    # Yellow
        (0, 255, 0),      # Green
        (0, 0, 255),      # Blue
        (75, 0, 130),     # Indigo
        (238, 130, 238),  # Violet
        (30, 30, 30),     # Dark gray
        (1, 1, 1)         # Almost black
    ]

    # Paddle settings
    PADDLE_WIDTH = 100
    PADDLE_HEIGHT = 20
    PADDLE_MOVE_SPEED = 10
    PADDLE_Y_OFFSET = 10

    # Ball settings
    BALL_RADIUS = 10
    BALL_INITIAL_SPEED = 3.5
    BALL_SPEED_INCREMENT = 0.05
    MAX_BALL_SPEED = 9
    BALL_START_Y_OFFSET = 50

    # Brick settings
    INITIAL_BRICK_ROWS = 4
    INITIAL_BRICK_COLS = 8
    BRICK_HEIGHT = 15
    BRICK_SPACING = 5
    FIRST_ROW_OFFSET = 42

    # Game settings
    INITIAL_LIVES = 3
    VICTORY_ROW_COUNT = 16
    POINTS_PER_BRICK = 10
    BOARD_CLEAR_BONUS = 7500

    # Auto-play settings
    AUTO_DEFLECT_MIN = 20
    AUTO_DEFLECT_MAX = 80
    AUTO_DEFLECT_X_FACTOR = 0.9


# ============================================================================
# GAME ENTITIES
# ============================================================================

class Paddle:
    """Represents the player's paddle"""

    def __init__(self, screen_width: int, screen_height: int):
        self.width = Config.PADDLE_WIDTH
        self.height = Config.PADDLE_HEIGHT
        self.move_speed = Config.PADDLE_MOVE_SPEED

        # Calculate starting position
        self.start_x = (screen_width - self.width) / 2
        self.start_y = screen_height - self.height - Config.PADDLE_Y_OFFSET

        self.x = self.start_x
        self.y = self.start_y
        self.speed = 0
        self.screen_width = screen_width

    def update(self, keys: pygame.key.ScancodeWrapper):
        """Update paddle position based on keyboard input"""
        if keys[pygame.K_LEFT]:
            self.speed = -self.move_speed
        elif keys[pygame.K_RIGHT]:
            self.speed = self.move_speed
        else:
            self.speed = 0

        self.x += self.speed

        # Keep paddle within screen bounds
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > self.screen_width:
            self.x = self.screen_width - self.width

    def set_position(self, x: float):
        """Set paddle x position directly (used for auto-play)"""
        self.x = max(0, min(x, self.screen_width - self.width))

    def draw(self, screen: pygame.Surface):
        """Draw the paddle"""
        pygame.draw.rect(screen, Config.WHITE, (self.x, self.y, self.width, self.height))

    def reset(self):
        """Reset paddle to starting position"""
        self.x = self.start_x
        self.y = self.start_y
        self.speed = 0

    def get_rect(self) -> pygame.Rect:
        """Get paddle rectangle for collision detection"""
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Ball:
    """Represents the game ball"""

    def __init__(self, screen_width: int, screen_height: int):
        self.radius = Config.BALL_RADIUS
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Calculate starting position
        self.start_x = screen_width / 2
        self.start_y = screen_height - Config.BALL_START_Y_OFFSET

        self.x = self.start_x
        self.y = self.start_y
        self.speed_x = Config.BALL_INITIAL_SPEED
        self.speed_y = -Config.BALL_INITIAL_SPEED
        self.speed_increment = Config.BALL_SPEED_INCREMENT
        self.max_speed = Config.MAX_BALL_SPEED

    def update(self):
        """Update ball position"""
        self.x += self.speed_x
        self.y += self.speed_y

    def check_wall_collision(self):
        """Check and handle collision with walls"""
        # Side walls
        if self.x <= 0 or self.x >= self.screen_width:
            self.speed_x = -self.speed_x

        # Top wall (brick area)
        if self.y <= Config.BRICK_HEIGHT:
            self.speed_y = -self.speed_y

    def check_paddle_collision(self, paddle: Paddle) -> bool:
        """Check and handle collision with paddle"""
        if (paddle.y <= self.y + self.radius <= paddle.y + paddle.height and
            paddle.x <= self.x <= paddle.x + paddle.width):

            # Calculate deflection angle based on where ball hits paddle
            contact_point = (self.x - paddle.x) / paddle.width
            deflection = (contact_point - 0.5) * 2

            self.speed_x = deflection * self.max_speed
            self.speed_y = -abs(self.speed_y)

            # Increase speed
            if abs(self.speed_x) < self.max_speed:
                self.speed_x += self.speed_increment if self.speed_x > 0 else -self.speed_increment
            if abs(self.speed_y) < self.max_speed:
                self.speed_y += self.speed_increment if self.speed_y > 0 else -self.speed_increment

            return True
        return False

    def is_out_of_bounds(self) -> bool:
        """Check if ball has fallen off the bottom"""
        return self.y > self.screen_height

    def draw(self, screen: pygame.Surface):
        """Draw the ball"""
        pygame.draw.circle(screen, Config.WHITE, (int(self.x), int(self.y)), self.radius)

    def reset(self):
        """Reset ball to starting position"""
        self.x = self.start_x
        self.y = self.start_y
        self.speed_x = Config.BALL_INITIAL_SPEED
        self.speed_y = -Config.BALL_INITIAL_SPEED

    def get_rect(self) -> pygame.Rect:
        """Get ball rectangle for collision detection"""
        return pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )


class Brick:
    """Represents a single brick"""

    def __init__(self, rect: pygame.Rect, color: Tuple[int, int, int]):
        self.rect = rect
        self.color = color

    def draw(self, screen: pygame.Surface):
        """Draw the brick"""
        pygame.draw.rect(screen, self.color, self.rect)


class BrickManager:
    """Manages the collection of bricks"""

    def __init__(self, screen_width: int):
        self.screen_width = screen_width
        self.rows = Config.INITIAL_BRICK_ROWS
        self.cols = Config.INITIAL_BRICK_COLS
        self.bricks: List[Brick] = []
        self.initialize_bricks()

    def initialize_bricks(self):
        """Create a new set of bricks"""
        self.bricks = []
        brick_width = self.screen_width // self.cols - Config.BRICK_SPACING

        for i in range(self.rows):
            for j in range(self.cols):
                x = j * (brick_width + Config.BRICK_SPACING) + 2.5
                y = (i * (Config.BRICK_HEIGHT + Config.BRICK_SPACING) + 2.5) + Config.FIRST_ROW_OFFSET
                rect = pygame.Rect(x, y, brick_width, Config.BRICK_HEIGHT)
                color = Config.COLORS[i % len(Config.COLORS)]
                self.bricks.append(Brick(rect, color))

    def check_collision(self, ball: Ball) -> bool:
        """Check if ball collides with any brick and remove it"""
        ball_rect = ball.get_rect()
        for brick in self.bricks[:]:
            if ball_rect.colliderect(brick.rect):
                self.bricks.remove(brick)
                ball.speed_y = -ball.speed_y
                return True
        return False

    def is_empty(self) -> bool:
        """Check if all bricks are cleared"""
        return len(self.bricks) == 0

    def get_first_brick(self) -> Optional[pygame.Rect]:
        """Get the first brick (used for auto-play targeting)"""
        if self.bricks:
            return self.bricks[0].rect
        return None

    def increase_difficulty(self):
        """Increase number of brick rows and columns"""
        self.rows += 1
        self.cols += 1
        self.initialize_bricks()

    def draw_all(self, screen: pygame.Surface):
        """Draw all bricks"""
        for brick in self.bricks:
            brick.draw(screen)


# ============================================================================
# GAME STATE MANAGEMENT
# ============================================================================

class GameState:
    """Manages game state including score, lives, and game status"""

    def __init__(self):
        self.score = 0
        self.lives = Config.INITIAL_LIVES
        self.rows_cleared = 0
        self.game_over = False
        self.victory = False

    def add_score(self, points: int):
        """Add points to score"""
        self.score += points

    def lose_life(self) -> bool:
        """Lose a life, returns True if game over"""
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True
            return True
        return False

    def add_life(self):
        """Add an extra life"""
        self.lives += 1

    def clear_board(self):
        """Handle board clear event"""
        self.rows_cleared += 1
        self.add_life()
        bonus = Config.BOARD_CLEAR_BONUS * self.rows_cleared
        self.add_score(bonus)

    def check_victory(self, brick_rows: int) -> bool:
        """Check if victory condition is met"""
        if brick_rows > Config.VICTORY_ROW_COUNT:
            self.victory = True
            return True
        return False

    def reset(self):
        """Reset game state"""
        self.score = 0
        self.lives = Config.INITIAL_LIVES
        self.rows_cleared = 0
        self.game_over = False
        self.victory = False


class AutoPlay:
    """Handles auto-play AI logic"""

    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.deflect_offset = 40

    def toggle(self):
        """Toggle auto-play on/off"""
        self.enabled = not self.enabled

    def calculate_deflect(self, paddle_x: float, target_x: float, screen_width: int) -> float:
        """Calculate optimal deflection offset for paddle positioning"""
        delta_x = target_x - paddle_x
        x_factor = Config.AUTO_DEFLECT_X_FACTOR

        min_deflect = Config.AUTO_DEFLECT_MIN
        max_deflect = Config.AUTO_DEFLECT_MAX
        mid_deflect = (min_deflect + max_deflect) / 2

        if delta_x == 0:
            return mid_deflect
        elif delta_x > 0:
            proportion = delta_x / (screen_width / 2) * x_factor
            return mid_deflect + (max_deflect - mid_deflect) * min(proportion, 1)
        else:
            proportion = abs(delta_x) / (screen_width / 2) * x_factor
            return mid_deflect - (mid_deflect - min_deflect) * min(proportion, 1)

    def update_paddle(self, paddle: Paddle, ball: Ball, target_brick: Optional[pygame.Rect], screen_width: int):
        """Update paddle position for auto-play"""
        if not self.enabled:
            return

        if target_brick:
            self.deflect_offset = self.calculate_deflect(paddle.x, target_brick.x, screen_width)

        paddle.set_position(ball.x - self.deflect_offset)


class GameLogger:
    """Handles game statistics logging"""

    @staticmethod
    def log_game(duration: float, score: int, lives: int, auto_play: bool):
        """Log game statistics to file"""
        # Convert duration to minutes and seconds
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        duration_str = f"{minutes} minutes {seconds} seconds"

        # Ensure logs directory exists
        logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        log_filename = os.path.join(logs_dir, "game-log.txt")

        # Create log entry
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_log_entry = (
            f"Game Ended: {current_time}\n"
            f"Auto Play: {auto_play}\n"
            f"Duration: {duration_str}\n"
            f"Lives Remaining: {lives}\n"
            f"Score: {score}\n"
            f"-----\n"
        )

        # Prepend to existing log file
        existing_contents = ""
        if os.path.exists(log_filename):
            with open(log_filename, "r") as file:
                existing_contents = file.read()

        with open(log_filename, "w") as file:
            file.write(new_log_entry + existing_contents)


# ============================================================================
# MAIN GAME CLASS
# ============================================================================

class Game:
    """Main game coordinator class"""

    def __init__(self, auto_play: bool = False):
        # Initialize Pygame
        pygame.init()

        # Setup display
        self.screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        pygame.display.set_caption("Brick Addiction v2.0")

        # Setup clock
        self.clock = pygame.time.Clock()

        # Setup font
        self.font = pygame.font.Font(None, 36)

        # Create game objects
        self.paddle = Paddle(Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)
        self.ball = Ball(Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)
        self.brick_manager = BrickManager(Config.SCREEN_WIDTH)
        self.game_state = GameState()
        self.auto_play = AutoPlay(auto_play)

        # Timing
        self.start_time = time.time()
        self.running = True

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_state.game_over:
                    self.reset_game()

    def update(self):
        """Update game logic"""
        if self.game_state.game_over or self.game_state.victory:
            return

        # Update paddle (manual or auto)
        if not self.auto_play.enabled:
            keys = pygame.key.get_pressed()
            self.paddle.update(keys)
        else:
            target_brick = self.brick_manager.get_first_brick()
            self.auto_play.update_paddle(
                self.paddle,
                self.ball,
                target_brick,
                Config.SCREEN_WIDTH
            )

        # Update ball
        self.ball.update()
        self.ball.check_wall_collision()

        # Check paddle collision
        if self.ball.check_paddle_collision(self.paddle):
            # Update auto-play deflect after paddle hit
            if self.auto_play.enabled:
                target_brick = self.brick_manager.get_first_brick()
                if target_brick:
                    self.auto_play.deflect_offset = self.auto_play.calculate_deflect(
                        self.paddle.x,
                        target_brick.x,
                        Config.SCREEN_WIDTH
                    )

        # Check brick collision
        if self.brick_manager.check_collision(self.ball):
            points = Config.POINTS_PER_BRICK * max(self.game_state.rows_cleared * 2, 1)
            self.game_state.add_score(points)

        # Check if ball is out of bounds
        if self.ball.is_out_of_bounds():
            if self.game_state.lose_life():
                return
            self.reset_ball_and_paddle()

        # Check if all bricks cleared
        if self.brick_manager.is_empty():
            self.game_state.clear_board()
            self.brick_manager.increase_difficulty()
            self.reset_ball_and_paddle()

            # Check victory condition
            self.game_state.check_victory(self.brick_manager.rows)

    def draw(self):
        """Draw everything"""
        self.screen.fill(Config.BLACK)

        if not self.game_state.game_over and not self.game_state.victory:
            # Draw game objects
            self.paddle.draw(self.screen)
            self.ball.draw(self.screen)
            self.brick_manager.draw_all(self.screen)
        elif self.game_state.victory:
            # Draw victory screen
            victory_text = self.font.render("VICTORY! YOU ARE A BRICKS ADDICT.", True, Config.WHITE)
            self.screen.blit(
                victory_text,
                (Config.SCREEN_WIDTH / 2 - victory_text.get_width() / 2,
                 Config.SCREEN_HEIGHT / 2 - victory_text.get_height() / 2)
            )
        else:
            # Draw game over screen
            self.brick_manager.draw_all(self.screen)
            game_over_text = self.font.render("GAME OVER", True, Config.WHITE)
            self.screen.blit(
                game_over_text,
                (Config.SCREEN_WIDTH / 2 - game_over_text.get_width() / 2,
                 Config.SCREEN_HEIGHT / 2 - game_over_text.get_height() / 2)
            )

        # Draw HUD
        score_text = self.font.render(f"Score: {self.game_state.score}", True, Config.WHITE)
        lives_text = self.font.render(f"Lives: {self.game_state.lives}", True, Config.WHITE)
        self.screen.blit(score_text, (30, 10))
        self.screen.blit(lives_text, (Config.SCREEN_WIDTH - 120, 10))

        pygame.display.flip()

    def reset_ball_and_paddle(self):
        """Reset ball and paddle to starting positions"""
        self.ball.reset()
        self.paddle.reset()

    def reset_game(self):
        """Reset entire game"""
        self.game_state.reset()
        self.brick_manager.rows = Config.INITIAL_BRICK_ROWS
        self.brick_manager.cols = Config.INITIAL_BRICK_COLS
        self.brick_manager.initialize_bricks()
        self.reset_ball_and_paddle()
        self.start_time = time.time()

    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(Config.FPS)

        # Log game statistics
        end_time = time.time()
        game_duration = end_time - self.start_time
        GameLogger.log_game(
            game_duration,
            self.game_state.score,
            self.game_state.lives,
            self.auto_play.enabled
        )

        # Cleanup
        pygame.quit()
        sys.exit()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Set auto_play to True to enable AI mode
    auto_play = False

    game = Game(auto_play=auto_play)
    game.run()
