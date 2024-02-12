import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up display
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (238, 130, 238)]

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
ball_start_x = screen_width / 2
ball_start_y = screen_height / 2
ball_x = ball_start_x
ball_y = ball_start_y
ball_radius = 10
ball_speed_x = 3
ball_speed_y = -3
ball_speed_increment = 0.1
max_ball_speed = 10

# Brick setup
brick_rows = 1
brick_cols = 10
brick_width = screen_width // brick_cols - 5
brick_height = 15

# Initialize bricks function
def initialize_bricks():
    bricks = []
    for i in range(brick_rows):
        for j in range(brick_cols):
            bricks.append((pygame.Rect(j * (brick_width + 5) + 2.5, i * (brick_height + 5) + 2.5, brick_width, brick_height), COLORS[i % len(COLORS)]))
    return bricks

bricks = initialize_bricks()

# Score and Lives
score = 0
lives = 3
font = pygame.font.Font(None, 36)

# Clock to control game speed
clock = pygame.time.Clock()
fps = 60

# Reset function to reset ball and paddle positions
def reset_ball_and_paddle():
    global paddle_x, paddle_y, ball_x, ball_y, ball_speed_x, ball_speed_y
    paddle_x, paddle_y = paddle_start_x, paddle_start_y
    ball_x, ball_y = ball_start_x, ball_start_y

# Game loop
running = True
game_over = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                paddle_speed = -paddle_move_speed
            elif event.key == pygame.K_RIGHT:
                paddle_speed = paddle_move_speed
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                paddle_speed = 0

    if not game_over:
        paddle_x += paddle_speed
        if paddle_x < 0:
            paddle_x = 0
        elif paddle_x + paddle_width > screen_width:
            paddle_x = screen_width - paddle_width
        
        ball_x += ball_speed_x
        ball_y += ball_speed_y
        if ball_x <= 0 or ball_x >= screen_width:
            ball_speed_x = -ball_speed_x
        if ball_y <= 0:
            ball_speed_y = -ball_speed_y
        if ball_y - ball_radius > screen_height:
            lives -= 1
            if lives <= 0:
                game_over = True
            reset_ball_and_paddle()
        
        if paddle_y <= ball_y + ball_radius <= paddle_y + paddle_height and paddle_x <= ball_x <= paddle_x + paddle_width:
            contact_point = (ball_x - paddle_x) / paddle_width
            deflection = (contact_point - 0.5) * 2
            ball_speed_x = deflection * max_ball_speed
            ball_speed_y = -abs(ball_speed_y)
            if abs(ball_speed_x) < max_ball_speed:
                ball_speed_x += ball_speed_increment if ball_speed_x > 0 else -ball_speed_increment
            if abs(ball_speed_y) < max_ball_speed:
                ball_speed_y += ball_speed_increment if ball_speed_y > 0 else -ball_speed_increment

        ball_rect = pygame.Rect(ball_x - ball_radius, ball_y - ball_radius, ball_radius * 2, ball_radius * 2)
        for brick, color in bricks[:]:
            if ball_rect.colliderect(brick):
                bricks.remove((brick, color))
                ball_speed_y = -ball_speed_y
                score += 10

        if not bricks:  # All bricks are cleared
            bricks = initialize_bricks()  # Reset bricks without changing anything else

    # Drawing
    screen.fill(BLACK)
    if not game_over:
        pygame.draw.rect(screen, WHITE, (paddle_x, paddle_y, paddle_width, paddle_height))
        pygame.draw.circle(screen, WHITE, (int(ball_x), int(ball_y)), ball_radius)
        for brick, color in bricks:
            pygame.draw.rect(screen, color, brick)
    else:
        game_over_text = font.render("GAME OVER", True, WHITE)
        screen.blit(game_over_text, (screen_width / 2 - game_over_text.get_width() / 2, screen_height / 2 - game_over_text.get_height() / 2))
    
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (screen_width - 100, 10))

    pygame.display.flip()
    clock.tick(fps)

# Quit Pygame
pygame.quit()
sys.exit()
