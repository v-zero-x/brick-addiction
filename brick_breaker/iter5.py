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
COLORS = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (238, 130, 238)]  # RGB for rainbow colors

# Paddle
paddle_width = 100
paddle_height = 20
paddle_x = (screen_width - paddle_width) / 2
paddle_y = screen_height - paddle_height - 10
paddle_speed = 0
paddle_move_speed = 10

# Ball
ball_x = screen_width / 2
ball_y = screen_height / 2
ball_radius = 10
ball_speed_x = 3  # Starting speed slower
ball_speed_y = -3  # Starting speed slower
ball_speed_increment = 0.5  # Increment speed by 0.5
max_ball_speed = 10  # Maximum speed to prevent the ball from becoming too fast to track

# Bricks
brick_rows = 7
brick_cols = 10
brick_width = screen_width // brick_cols - 5
brick_height = 15
bricks = []
for i in range(brick_rows):
    for j in range(brick_cols):
        bricks.append((pygame.Rect(j * (brick_width + 5) + 2.5, i * (brick_height + 5) + 2.5, brick_width, brick_height), COLORS[i % len(COLORS)]))

# Score
score = 0
font = pygame.font.Font(None, 36)

# Game loop
running = True
bricks_broken = 0  # Keep track of the number of bricks broken
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
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                paddle_speed = 0
    
    # Move paddle
    paddle_x += paddle_speed
    if paddle_x < 0:
        paddle_x = 0
    elif paddle_x + paddle_width > screen_width:
        paddle_x = screen_width - paddle_width
    
    # Move ball
    ball_x += ball_speed_x
    ball_y += ball_speed_y
    if ball_x <= 0 or ball_x >= screen_width:
        ball_speed_x = -ball_speed_x
    if ball_y <= 0:
        ball_speed_y = -ball_speed_y
    # Bounce off paddle
    if paddle_y <= ball_y + ball_radius <= paddle_y + paddle_height and paddle_x <= ball_x <= paddle_x + paddle_width:
        ball_speed_y = -ball_speed_y
    
    # Collision with bricks
    ball_rect = pygame.Rect(ball_x - ball_radius, ball_y - ball_radius, ball_radius * 2, ball_radius * 2)
    for brick, color in bricks[:]:
        if ball_rect.colliderect(brick):
            bricks.remove((brick, color))
            ball_speed_y = -ball_speed_y
            score += 10
            bricks_broken += 1
    
    # Increase ball speed based on bricks broken or time
    if bricks_broken and bricks_broken % 5 == 0:  # Every 5 bricks broken, increase speed
        bricks_broken += 1  # Ensure speed only increases once per milestone
        if abs(ball_speed_x) < max_ball_speed:
            ball_speed_x += ball_speed_increment if ball_speed_x > 0 else -ball_speed_increment
        if abs(ball_speed_y) < max_ball_speed:
            ball_speed_y += ball_speed_increment if ball_speed_y > 0 else -ball_speed_increment
    
    # Fill the screen with black
    screen.fill(BLACK)
    
    # Draw paddle
    pygame.draw.rect(screen, WHITE, (paddle_x, paddle_y, paddle_width, paddle_height))
    
    # Draw ball
    pygame.draw.circle(screen, WHITE, (int(ball_x), int(ball_y)), ball_radius)
    
    # Draw bricks with colors
    for brick, color in bricks:
        pygame.draw.rect(screen, color, brick)
    
    # Display score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
