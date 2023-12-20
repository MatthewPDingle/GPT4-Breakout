import pygame
import math
import numpy
from pygame.math import Vector2

def create_beep_sound(frequency=440, duration=100):
    # Frequency in Hz, Duration in milliseconds
    sample_rate = 44100
    amplitude = 4096
    num_samples = int(sample_rate * duration / 1000.0)

    buf = numpy.zeros((num_samples, 2), dtype = numpy.int16)
    max_sample = 2**(16 - 1) - 1

    for s in range(num_samples):
        t = float(s) / sample_rate    # Time in seconds
        buf[s][0] = int(amplitude * numpy.sin(2 * numpy.pi * frequency * t))  # Left channel
        buf[s][1] = int(amplitude * numpy.sin(2 * numpy.pi * frequency * t))  # Right channel

    sound = pygame.sndarray.make_sound(buf)
    return sound

class Paddle:
    def __init__(self, screen_width, screen_height, width=100, height=15):
        self.width = width
        self.height = height
        self.position = Vector2(screen_width // 2 - width // 2, screen_height - height)
        self.color = (255, 255, 255)

    def move(self, mouse_x, screen_width):
        self.position.x = max(min(mouse_x - self.width // 2, screen_width - self.width), 0)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (*self.position, self.width, self.height))

class Ball:
    def __init__(self, screen_width, screen_height, radius=10, speed=5):
        self.radius = radius
        self.speed = speed
        self.position = Vector2(screen_width // 2, screen_height // 2)
        self.velocity = Vector2(speed, -speed)
        self.color = (255, 255, 255)

    def move(self):
        self.position += self.velocity

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.position.x), int(self.position.y)), self.radius)

class Brick:
    def __init__(self, position, width=50, height=20, color=(255, 0, 0)):
        self.position = position
        self.width = width
        self.height = height
        self.color = color
        self.active = True

    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, self.color, (*self.position, self.width, self.height))

class GameManager:
    def __init__(self):
        pygame.init()
        self.init_game_properties()
        self.load_resources()
        self.reset_game(initial=True)

    def init_game_properties(self):
        self.screen_width, self.screen_height = 800, 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Breakout Game")
        self.font = pygame.font.SysFont(None, 24)
        self.paddle = Paddle(self.screen_width, self.screen_height)
        self.ball = Ball(self.screen_width, self.screen_height)
        self.bricks = self.create_bricks()
        self.score = 0
        self.running = True
        self.game_started = False
        self.game_over = False
        self.game_won = False

    def load_resources(self):
        self.bounce_sound = create_beep_sound(frequency=440, duration=100)

    def create_bricks(self):
        bricks = []
        # Define colors and corresponding points
        color_points_map = {
            (255, 0, 0): 5,   # Red bricks
            (0, 255, 0): 4,   # Green bricks
            (0, 0, 255): 3,   # Blue bricks
            (255, 165, 0): 2, # Orange bricks
            (255, 255, 0): 1  # Yellow bricks
        }
        colors = list(color_points_map.keys())

        for i in range(5):  # 5 rows
            for j in range(16):  # 16 columns
                color = colors[i]
                brick = Brick(Vector2(j * 50, i * 20 + 50), color=color)
                brick.points = color_points_map[color]  # Assign points based on color
                bricks.append(brick)

        return bricks

    def run(self):
        self.show_start_screen()
        while self.running:
            self.handle_events()
            if self.game_started and not (self.game_over or self.game_won):
                self.update_game_state()
            self.draw_game_screen()
            pygame.time.Clock().tick(60)

    def show_start_screen(self):
        self.draw_start_screen()
        self.wait_for_start()
            
    def wait_for_start(self):
        while not self.game_started:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse click
                    self.game_started = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif self.game_over or self.game_won:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse click
                    self.reset_game()

    def draw_game_screen(self):
        self.screen.fill((0, 0, 0))  # Clear screen
        self.paddle.draw(self.screen)
        self.ball.draw(self.screen)
        for brick in self.bricks:
            brick.draw(self.screen)
        self.draw_score()
        if self.game_over:
            self.draw_game_over_screen()
        elif self.game_won:
            self.draw_win_screen()
        pygame.display.flip()

    def check_collisions(self):
        # Ball and screen boundaries
        if self.ball.position.x <= self.ball.radius:
            self.ball.velocity.x *= -1
            self.ball.position.x = self.ball.radius  # Nudge the ball away from the left edge
            self.bounce_sound.play()
            self.normalize_ball_velocity()
        elif self.ball.position.x >= self.screen_width - self.ball.radius:
            self.ball.velocity.x *= -1
            self.ball.position.x = self.screen_width - self.ball.radius  # Nudge the ball away from the right edge
            self.bounce_sound.play()
            self.normalize_ball_velocity()

        if self.ball.position.y <= self.ball.radius:
            self.ball.velocity.y *= -1
            self.ball.position.y = self.ball.radius  # Nudge the ball away from the top edge
            self.bounce_sound.play()
            self.normalize_ball_velocity()

        # Ball and paddle
        if self.paddle_collision():
            # Calculate the offset from the center of the paddle
            offset = (self.ball.position.x - self.paddle.position.x) / self.paddle.width - 0.5

            # Adjust the ball's velocity based on the offset and the maximum bounce angle
            self.adjust_ball_velocity_for_paddle_collision(offset)
            self.bounce_sound.play()

        # Ball and bricks
        for brick in self.bricks:
            if brick.active and self.brick_collision(brick):
                self.handle_brick_collision(brick)
                break  # Break after handling the first collision

    def normalize_ball_velocity(self):
        speed = self.ball.speed
        self.ball.velocity = self.ball.velocity.normalize() * speed

    def paddle_collision(self):
        # Check if the ball is within the vertical range of the paddle
        if self.ball.position.y + self.ball.radius >= self.paddle.position.y:
            # Check if the ball is within the horizontal range of the paddle
            if self.paddle.position.x - self.ball.radius <= self.ball.position.x <= self.paddle.position.x + self.paddle.width + self.ball.radius:
                return True
        return False

    def handle_brick_collision(self, brick):
        brick.active = False
        self.score += brick.points
        self.bounce_sound.play()

        # Calculate the collision side considering the ball's direction
        collision_side = self.calculate_collision_side_with_direction(brick)

        # Adjust the ball's velocity based on the collision side
        if collision_side == "top" and self.ball.velocity.y > 0:
            self.ball.velocity.y *= -1
        elif collision_side == "bottom" and self.ball.velocity.y < 0:
            self.ball.velocity.y *= -1
        elif collision_side == "left" and self.ball.velocity.x > 0:
            self.ball.velocity.x *= -1
        elif collision_side == "right" and self.ball.velocity.x < 0:
            self.ball.velocity.x *= -1

        self.normalize_ball_velocity()
        
    def calculate_collision_side_with_direction(self, brick):
        ball_center = self.ball.position
        ball_direction = self.ball.velocity
        brick_rect = pygame.Rect(brick.position.x, brick.position.y, brick.width, brick.height)

        # Determine the likely side of collision based on the direction of the ball
        if ball_direction.y > 0:  # Moving down
            if ball_center.y < brick_rect.top:
                return "top"
        elif ball_direction.y < 0:  # Moving up
            if ball_center.y > brick_rect.bottom:
                return "bottom"

        if ball_direction.x > 0:  # Moving right
            if ball_center.x < brick_rect.left:
                return "left"
        elif ball_direction.x < 0:  # Moving left
            if ball_center.x > brick_rect.right:
                return "right"

        # Default to a vertical collision if the direction is not conclusive
        return "top" if ball_center.y < brick_rect.centery else "bottom"

    def brick_collision(self, brick):
        ball_rect = pygame.Rect(self.ball.position.x - self.ball.radius, self.ball.position.y - self.ball.radius, 
                                2 * self.ball.radius, 2 * self.ball.radius)
        brick_rect = pygame.Rect(brick.position.x, brick.position.y, brick.width, brick.height)
        return ball_rect.colliderect(brick_rect)

    def adjust_ball_velocity_for_paddle_collision(self, offset):
        # Maximum bounce angle of 70 degrees in radians
        max_bounce_angle = math.radians(70)

        # Calculate the new angle of the ball
        angle = max_bounce_angle * offset

        # Adjust the ball's x and y velocities based on this angle
        self.ball.velocity.x = self.ball.speed * math.sin(angle)
        self.ball.velocity.y = -self.ball.speed * math.cos(angle)

    def check_win_condition(self):
        if all(not brick.active for brick in self.bricks):
            self.game_won = True

    def reset_game(self, initial=False):
        if not initial:
            self.game_started = True
            self.game_over = False
            self.game_won = False
        self.position_ball_on_paddle()
        self.ball.velocity = Vector2(self.ball.speed, -self.ball.speed)
        if not initial:
            self.bricks = self.create_bricks()
            self.score = 0

    def position_ball_on_paddle(self):
        paddle_top = self.screen_height - self.paddle.height - self.ball.radius
        self.ball.position = Vector2(self.paddle.position.x + self.paddle.width / 2, paddle_top)
    
    def update_game_state(self):
        self.paddle.move(pygame.mouse.get_pos()[0], self.screen_width)
        self.ball.move()
        self.check_collisions()
        self.check_win_condition()
        if self.ball.position.y - self.ball.radius > self.screen_height:
            self.game_over = True

    def draw_score(self):
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (5, 5))

    def draw_game_over_screen(self):
        self.display_centered_text("GAME OVER", self.screen_height // 2 - 30)
        self.display_centered_text(f"Final Score: {self.score}", self.screen_height // 2)
        self.display_centered_text("Click to Restart", self.screen_height // 2 + 30)

    def draw_win_screen(self):
        self.display_centered_text("Congratulations, you win!", 50)
        self.display_centered_text(f"Final Score: {self.score}", 80)
        self.display_centered_text("Click to Restart", 110)  # Updated text for consistency

    def draw_start_screen(self):
        self.screen.fill((0, 0, 0))  # Clear screen
        self.display_centered_text("Click to Start", self.screen_height // 2)
        pygame.display.flip()
        
    def display_centered_text(self, text, y_offset):
        text_surface = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, y_offset))
        self.screen.blit(text_surface, text_rect)

# Main execution
if __name__ == "__main__":
    game_manager = GameManager()
    game_manager.run()