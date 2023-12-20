import pygame
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
BALL_RADIUS = 10
BRICK_WIDTH = 50
BRICK_HEIGHT = 20
BRICK_ROWS = 5
BRICK_COLS = 16
PADDLE_SPEED = 5
BALL_SPEED = 0.3
BRICK_START_Y = 50
MAX_BOUNCE_ANGLE = math.radians(70)

# Colors
WHITE = (255, 255, 255)
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 165, 0), (255, 255, 0)]
POINTS = [5, 4, 3, 2, 1]

# Setup the screen and font
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Breakout Game")
font = pygame.font.SysFont(None, 24)

# Initialize bricks and score
bricks = [[True for _ in range(BRICK_COLS)] for _ in range(BRICK_ROWS)]
score = 0

# Function definitions
def draw_game_over_screen(score):
    screen.fill((0, 0, 0))  # Clear screen
    # Display Game Over message
    game_over_text = font.render("GAME OVER", True, WHITE)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    restart_text = font.render("Press Enter to Play Again", True, WHITE)
    
    # Positioning text on screen
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 30))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

    pygame.display.flip()

def draw_start_screen():
    screen.fill((0, 0, 0))  # Clear screen
    start_text = font.render("Press Enter to Play", True, WHITE)
    screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 - start_text.get_height() // 2))
    pygame.display.flip()

def draw_win_screen(score):
    screen.fill((0, 0, 0))  # Clear screen
    win_text = font.render("Congratulations, you win!", True, WHITE)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    restart_text = font.render("Press Enter to Play Again", True, WHITE)

    screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - win_text.get_height() // 2))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 30))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

    pygame.display.flip()  

def check_for_win():
    for row in bricks:
        if any(row):
            return False
    return True

def adjust_ball_speed(dx, dy):
    # Calculate the current speed and angle
    speed = math.sqrt(dx**2 + dy**2)
    angle = math.atan2(dy, dx)

    # Adjust dx and dy to maintain the constant BALL_SPEED
    dx = BALL_SPEED * math.cos(angle)
    dy = BALL_SPEED * math.sin(angle)

    return dx, dy

def reset_ball():
    return SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, BALL_SPEED_X, BALL_SPEED_Y

def draw_paddle(x):
    pygame.draw.rect(screen, WHITE, (x, SCREEN_HEIGHT - PADDLE_HEIGHT, PADDLE_WIDTH, PADDLE_HEIGHT))

def draw_ball(x, y):
    pygame.draw.circle(screen, WHITE, (x, y), BALL_RADIUS)

def draw_bricks():
    for i in range(BRICK_ROWS):
        for j in range(BRICK_COLS):
            if bricks[i][j]:
                pygame.draw.rect(screen, COLORS[i], (j * BRICK_WIDTH, i * BRICK_HEIGHT + BRICK_START_Y, BRICK_WIDTH, BRICK_HEIGHT))

def draw_score(score):
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (5, 5))

def move_ball(x, y, dx, dy):
    global score
    x += dx
    y += dy

    # Collision with walls
    if x <= BALL_RADIUS or x >= SCREEN_WIDTH - BALL_RADIUS:
        dx = -dx
    if y <= BALL_RADIUS:
        dy = -dy

    # Collision with paddle
    if y >= SCREEN_HEIGHT - PADDLE_HEIGHT - BALL_RADIUS and paddle_x - BALL_RADIUS <= x <= paddle_x + PADDLE_WIDTH + BALL_RADIUS:
        hit_position = (x - (paddle_x + PADDLE_WIDTH / 2)) / (PADDLE_WIDTH / 2)
        bounce_angle = hit_position * MAX_BOUNCE_ANGLE
        dx = BALL_SPEED * math.sin(bounce_angle)
        dy = -BALL_SPEED * math.cos(bounce_angle)

    # Collision with bricks
    for i in range(BRICK_ROWS):
        for j in range(BRICK_COLS):
            if bricks[i][j]:
                brick_x = j * BRICK_WIDTH
                brick_y = i * BRICK_HEIGHT + BRICK_START_Y
                if (brick_x - BALL_RADIUS <= x <= brick_x + BRICK_WIDTH + BALL_RADIUS and 
                    brick_y - BALL_RADIUS <= y <= brick_y + BRICK_HEIGHT + BALL_RADIUS):
                    bricks[i][j] = False
                    # Determine if the collision is vertical or horizontal
                    if x < brick_x or x > brick_x + BRICK_WIDTH:
                        dx = -dx
                    else:
                        dy = -dy
                    score += POINTS[i]
                    return x, y, dx, dy

    return x, y, dx, dy

def main():
    global paddle_x, bricks, score
    running = True
    game_started = False
    game_over = False
    game_won = False
    paddle_x = SCREEN_WIDTH // 2
    ball_x, ball_y, ball_dx, ball_dy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, BALL_SPEED, -BALL_SPEED

    draw_start_screen()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if not game_started and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                game_started = True
            if (game_over or game_won) and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                game_over = False
                game_won = False
                ball_x, ball_y, ball_dx, ball_dy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, BALL_SPEED, -BALL_SPEED
                score = 0
                bricks = [[True for _ in range(BRICK_COLS)] for _ in range(BRICK_ROWS)]

        if game_started and not game_over and not game_won:
            # Mouse Control
            mouse_x = pygame.mouse.get_pos()[0]
            paddle_x = mouse_x - PADDLE_WIDTH // 2

            # Keep paddle within screen boundaries
            paddle_x = max(paddle_x, 0)
            paddle_x = min(paddle_x, SCREEN_WIDTH - PADDLE_WIDTH)

            ball_x, ball_y, ball_dx, ball_dy = move_ball(ball_x, ball_y, ball_dx, ball_dy)

            if ball_y > SCREEN_HEIGHT:
                game_over = True
            elif not any(sum(row) for row in bricks):
                game_won = True

            screen.fill((0, 0, 0))
            draw_paddle(paddle_x)
            draw_ball(ball_x, ball_y)
            draw_bricks()
            draw_score(score)

        elif game_over:
            draw_game_over_screen(score)
        elif game_won:
            draw_win_screen(score)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()