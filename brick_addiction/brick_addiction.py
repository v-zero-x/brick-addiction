# Python v3.11.5
# Brick Addiction v0.1

import pygame
import sys
import random
import datetime
import os
import time

auto_play = False
auto_deflect = 40
# Game Speed
fps = 60

# Initialize Pygame
pygame.init()

# Set up display
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (238, 130, 238), (30, 30, 30), (1, 1 ,1)]

# Paddle initial positions and settings
paddle_width = 100
paddle_height = 20
paddle_start_x = (screen_width - paddle_width) / 2
paddle_start_y = screen_height - paddle_height - 10
paddle_x = paddle_start_x
paddle_y = paddle_start_y
paddle_speed = 0
paddle_move_speed = 10

# Ball initial positions and settings
# ball_start_x = screen_width / 2
# ball_start_y = screen_height / 2
ball_start_x = screen_width / 2
ball_start_y = screen_height - 50
ball_x = ball_start_x
ball_y = ball_start_y
ball_radius = 10
ball_speed_x = 3.5
ball_speed_y = -3.5
ball_speed_increment = 0.05 # initial 0.05
max_ball_speed = 9

# Brick setup
brick_rows = 4 # 4
brick_cols = 8 # 8
rows_cleared = 0
brick_width = screen_width // brick_cols - 5
brick_height = 15

# Initialize bricks function
def initialize_bricks(brick_rows, brick_cols):
    bricks = []
    first_row_offset = 42
    for i in range(brick_rows):
        for j in range(brick_cols):
            bricks.append((pygame.Rect(j * (brick_width + 5) + 2.5, 
                           (i * (brick_height + 5) + 2.5) + first_row_offset,
                           brick_width, brick_height), COLORS[i % len(COLORS)]))
    return bricks

bricks = initialize_bricks(brick_rows, brick_cols)

# Score and Lives
score = 0
lives = 3
font = pygame.font.Font(None, 36)

# Clock to control game speed
clock = pygame.time.Clock()

# Reset function to reset ball and paddle positions
def reset_ball_and_paddle():
    global paddle_x, paddle_y, ball_x, ball_y, ball_speed_x, ball_speed_y, ball_start_y
    paddle_x, paddle_y = paddle_start_x, paddle_start_x
    paddle_x, paddle_y = paddle_start_x, paddle_start_y
    ball_x, ball_y = ball_start_x, ball_start_y

def find_target_brick():
    if bricks:
        return bricks[0][0]
        # return random.choice(bricks)[0]  # Selects a random brick's rectangle
    return None

def calculate_auto_deflect(paddle_x, target_brick_x, screen_width):
    # Calculate delta_x
    delta_x = target_brick_x - paddle_x
    x_factor = 0.9
    # Define the range and midpoint for auto_deflect
    min_deflect, max_deflect = 20, 80
    mid_deflect = (min_deflect + max_deflect) / 2  # Midpoint is 50

    if delta_x == 0:
        # If delta_x is zero, set auto_deflect to the midpoint
        auto_deflect = mid_deflect
    elif delta_x > 0:
        # If delta_x is positive, scale auto_deflect between 50 and 80
        # The proportion is based on the ratio of delta_x to half the screen width (as the max expected delta)
        proportion = delta_x / (screen_width / 2) * x_factor
        auto_deflect = mid_deflect + (max_deflect - mid_deflect) * min(proportion, 1)
    else:
        # If delta_x is negative, scale auto_deflect between 20 and 50
        # The proportion is the absolute value of delta_x to half the screen width
        proportion = abs(delta_x) / (screen_width / 2) * x_factor
        auto_deflect = mid_deflect - (mid_deflect - min_deflect) * min(proportion, 1)
    return auto_deflect

def log_stats(duration, score):
    # Get the current date to use in the filename
    current_date = datetime.datetime.now().strftime("%Y%m%d-%H%M")

    # Convert duration from seconds to minutes and seconds
    minutes = int(duration // 60)
    seconds = int(duration % 60)
    duration_str = f"{minutes} minutes {seconds} seconds"

    # Define the logs directory path
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    
    # Check if the logs directory exists, if not, create it
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    log_filename = logs_dir + "/game-log.txt"

    # Capture the current time for the log entry
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Prepare new log entry
    new_log_entry = f"Game Ended: {current_time}\nAuto Play: {auto_play}\nDuration: {duration_str}\nLives Remaining: {lives}\nScore: {score}\n-----\n"
    
    # Check if the log file already exists and read its contents
    if os.path.exists(log_filename):
        with open(log_filename, "r") as file:
            existing_contents = file.read()
    else:
        existing_contents = ""
    
    # Write the new log entry at the beginning of the file, followed by the old contents
    with open(log_filename, "w") as file:
        file.write(new_log_entry + existing_contents)

def reset_game():
    global game_over, running, score, lives, bricks, rows_cleared
    game_over = False
    running = True
    score = 0
    lives = 3
    brick_rows = 4 # 4
    brick_cols = 8 # 8
    rows_cleared = 0
    bricks = initialize_bricks(brick_rows, brick_cols)


# Game loop
running = True
game_over = False
victory = False
start_time = time.time()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                paddle_speed = -paddle_move_speed
            elif event.key == pygame.K_RIGHT:
                paddle_speed = paddle_move_speed
            elif game_over and event.key == pygame.K_r:
                reset_game()
                continue
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                paddle_speed = 0

    if not game_over and not victory:
        paddle_x += paddle_speed
        if paddle_x < 0:
            paddle_x = 0
        elif paddle_x + paddle_width > screen_width:
            paddle_x = screen_width - paddle_width
        
        ball_x += ball_speed_x
        ball_y += ball_speed_y
        if ball_x <= 0 or ball_x >= screen_width:
            ball_speed_x = -ball_speed_x
        if ball_y <= (brick_height):
            ball_speed_y = -ball_speed_y
        if ball_y > screen_height:
            lives -= 1
            if lives <= 0:
                game_over = True
            reset_ball_and_paddle()
        
        # Ball is deflected
        # Note to ChatGPT: this code currently deflects the ball effectively. The code in this 'if block' should not be altered.
        if paddle_y <= ball_y + ball_radius <= paddle_y + paddle_height and paddle_x <= ball_x <= paddle_x + paddle_width:
            contact_point = (ball_x - paddle_x) / paddle_width
            deflection = (contact_point - 0.5) * 2
            ball_speed_x = deflection * max_ball_speed
            ball_speed_y = -abs(ball_speed_y)
            # if auto_play:
            #     ball_speed_increment = 2
            if abs(ball_speed_x) < max_ball_speed:
                ball_speed_x += ball_speed_increment if ball_speed_x > 0 else -ball_speed_increment
            if abs(ball_speed_y) < max_ball_speed:
                ball_speed_y += ball_speed_increment if ball_speed_y > 0 else -ball_speed_increment

            if auto_play:
                # auto_deflect = random.randint(20, 80)
                target_brick_x = find_target_brick()
                auto_deflect = calculate_auto_deflect(paddle_x, target_brick_x.x, screen_width)

        # Paddle tracks ball_x position on each game loop adding the last auto_deflect offset from the prior deflection
        if auto_play:
            paddle_x = ball_x - auto_deflect

        ball_rect = pygame.Rect(ball_x - ball_radius, ball_y - ball_radius, ball_radius * 2, ball_radius * 2)
        for brick, color in bricks[:]:
            if ball_rect.colliderect(brick):
                bricks.remove((brick, color))
                ball_speed_y = -ball_speed_y
                score += 10 * max(rows_cleared * 2, 1)
        if not bricks:  # All bricks are cleared
            lives += 1  # Give the player an extra life for clearing the board
            brick_rows += 1
            brick_cols += 1
            if(brick_rows > 16):
                victory = True

            reset_ball_and_paddle()
            brick_width = screen_width // brick_cols - 5
            bricks = initialize_bricks(brick_rows, brick_cols)  # Reset bricks without changing anything else
            
            # bonus points for clearing a row
            rows_cleared += 1
            score += 7500 * rows_cleared

    # Drawing
    screen.fill(BLACK)
    if not game_over and not victory:
        pygame.draw.rect(screen, WHITE, (paddle_x, paddle_y, paddle_width, paddle_height))
        pygame.draw.circle(screen, WHITE, (int(ball_x), int(ball_y)), ball_radius)
        for brick, color in bricks:
            pygame.draw.rect(screen, color, brick)
    elif victory:
        victory_text = font.render("VICTORY! YOU ARE A BRICKS ADDICT.", True, WHITE)
        screen.blit(victory_text, (screen_width / 2 - victory_text.get_width() / 2, screen_height / 2 - victory_text.get_height() / 2))
        score_text = font.render(f"Score: {score}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(score_text, (30, 10))
        # pygame.display.flip()
    else:
        for brick, color in bricks:
            pygame.draw.rect(screen, color, brick)
        game_over_text = font.render("GAME OVER", True, WHITE)
        screen.blit(game_over_text, (screen_width / 2 - game_over_text.get_width() / 2, screen_height / 2 - game_over_text.get_height() / 2))
        score_text = font.render(f"Score: {score}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(score_text, (30, 10))
        pygame.display.flip()
        continue
    
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(score_text, (30, 10))
    screen.blit(lives_text, (screen_width - 120, 10))

    pygame.display.flip()
    clock.tick(fps)

end_time = time.time()
game_duration = end_time - start_time
log_stats(game_duration, score)

# Quit Pygame
pygame.quit()
sys.exit()
