import pygame
import math
import numpy as np
import json
import os
from pygame.math import Vector2

def create_beep_sound(frequency=293.66, duration=100, volume=0.2):
    sample_rate = 44100
    num_samples = int(sample_rate * duration / 1000.0)
    
    # Generate a sine wave
    t = np.linspace(0, duration / 1000.0, num_samples, endpoint=False)
    wave = np.sin(2 * np.pi * frequency * t)

    # Apply a more gradual fade in and fade out (Hanning window)
    fade_length = int(sample_rate * 0.01)  # 10ms fade
    fade_in = np.hanning(fade_length * 2)[:fade_length]
    fade_out = np.hanning(fade_length * 2)[-fade_length:]
    wave[:fade_length] *= fade_in
    wave[-fade_length:] *= fade_out

    # Adjust volume
    wave *= volume

    # Convert to 16-bit and stereo
    max_amplitude = np.iinfo(np.int16).max
    wave = (wave * max_amplitude).astype(np.int16)
    stereo_wave = np.column_stack((wave, wave))  # Duplicate for stereo

    # Create and return the pygame sound object
    sound = pygame.sndarray.make_sound(stereo_wave)
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
        
    def increase_speed(self, percent_increase):
        self.speed *= (1 + percent_increase / 100)
        self.velocity = self.velocity.normalize() * self.speed

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
    color_points_map = {
        (255, 0, 0): 5,   # Red bricks
        (0, 255, 0): 4,   # Green bricks
        (0, 0, 255): 3,   # Blue bricks
        (255, 165, 0): 2, # Orange bricks
        (255, 255, 0): 1  # Yellow bricks
    }

    def __init__(self):
        pygame.init()
        self.level = 1  # Initialize the level attribute first
        self.init_game_properties()
        self.reset_game(initial=True)
        self.last_mouse_x = self.screen_width // 2  # Initialize with the screen center
        self.high_score = self.load_high_score()
        self.level_ready = False  # New attribute to indicate readiness to start the level
        self.bounce_sound = create_beep_sound()  # Default beep sound for bricks
        self.wall_paddle_bounce_sound = create_beep_sound(293.66)  # D note for walls and paddle

    def init_game_properties(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'  # Center the game window
        self.screen_width, self.screen_height = 800, 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Breakout Game")
        self.font = pygame.font.SysFont(None, 24)
        self.paddle = Paddle(self.screen_width, self.screen_height)
        self.ball = Ball(self.screen_width, self.screen_height)
        self.load_level(self.level)  # Now safe to call load_level
        self.score = 0
        self.running = True
        self.game_started = False
        self.game_over = False
        self.game_won = False

    def load_high_score(self):
        try:
            with open('stats.json', 'r') as file:
                data = json.load(file)
                return data.get('high_score', 0)
        except (FileNotFoundError, json.JSONDecodeError):
            return 0

    def save_high_score(self):
        with open('stats.json', 'w') as file:
            json.dump({'high_score': self.high_score}, file)

    def update_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()

    def load_level(self, level_number):
        self.level = level_number
        
        if level_number == 1:
            self.ball.speed = 5  # Reset to base speed
        else:
            self.ball.increase_speed(10)  # Increase speed by 10% for each new level

        if level_number == 1:
            self.bricks = self.create_level_1_bricks()
        elif level_number == 2:
            self.bricks = self.create_level_2_bricks()
        elif level_number == 3:
            self.bricks = self.create_level_3_bricks()
        elif level_number == 4:
            self.bricks = self.create_level_4_bricks()
        elif level_number == 5:
            self.bricks = self.create_level_5_bricks()

    def create_level_1_bricks(self):
        bricks = []
        colors = list(self.color_points_map.keys())

        for i in range(5):
            for j in range(16):
                color = colors[i]
                brick = Brick(Vector2(j * 50, i * 20 + 50), color=color)
                brick.points = self.color_points_map[color]
                bricks.append(brick)

        return bricks

    def create_level_2_bricks(self):
        bricks = []
        colors = list(self.color_points_map.keys())

        for i in range(5):
            for j in range(16):
                color_index = (i + j) % len(colors)
                color = colors[color_index]
                brick = Brick(Vector2(j * 50, i * 20 + 50), color=color)
                brick.points = self.color_points_map[color]
                bricks.append(brick)

        return bricks

    def create_level_3_bricks(self):
        bricks = []
        colors = list(self.color_points_map.keys())

        for i in range(3):
            for j in range(16):
                if j < 3 or j > 12 or (i == 1 and (j < 6 or j > 9)):
                    continue
                color = colors[i % len(colors)]
                brick = Brick(Vector2(j * 50, i * 20 + 50), color=color)
                brick.points = self.color_points_map[color]
                bricks.append(brick)

        offset_rows = 2 
        for i in range(3 + offset_rows, 5 + offset_rows): 
            for j in range(16):
                color_index = (j % len(colors))
                color = colors[color_index]
                brick = Brick(Vector2(j * 50, i * 20 + 50), color=color)
                brick.points = self.color_points_map[color]
                bricks.append(brick)

        return bricks

    def create_level_4_bricks(self):
        bricks = []
        colors = list(self.color_points_map.keys())
        max_row = 9

        for i in range(max_row):
            bricks_in_row = max_row - abs(max_row // 2 - i)
            start_col = (16 - bricks_in_row) // 2

            for j in range(bricks_in_row):
                color_index = (i + j) % len(colors)
                color = colors[color_index]
                brick = Brick(Vector2((start_col + j) * 50, i * 20 + 50), color=color)
                brick.points = self.color_points_map[color]
                bricks.append(brick)

        return bricks

    def create_level_5_bricks(self):
        bricks = []
        colors = list(self.color_points_map.keys())
        num_columns = 16

        for i in range(6):
            for j in range(num_columns):
                if j % 4 == 0 or (i % 2 == 0 and j % 4 == 2):
                    continue

                color_index = (i + j) % len(colors)
                color = colors[color_index]
                brick = Brick(Vector2(j * 50, i * 20 + 50), color=color)
                brick.points = self.color_points_map[color]
                bricks.append(brick)

        return bricks

    def run(self):
        self.show_start_screen()
        while self.running:
            self.handle_events()
            # Start the level on mouse click
            if self.game_started and not (self.game_over or self.game_won):
                self.update_game_state()
            self.draw_game_screen()
            pygame.time.Clock().tick(60)
            
    def play_brick_sound(self, color):
        # Define the frequencies for each color
        color_frequency_map = {
            (255, 255, 0): 329.63,  # Yellow (E note)
            (255, 165, 0): 349.23,  # Orange (F note)
            (0, 0, 255): 392.00,    # Blue (G note)
            (0, 255, 0): 440.00,    # Green (A note)
            (255, 0, 0): 493.88     # Red (B note)
        }
        frequency = color_frequency_map.get(color, 440)  # Default to A note if color not found
        sound = create_beep_sound(frequency=frequency, duration=100)
        sound.play()

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
            elif event.type == pygame.MOUSEMOTION:
                # Update the last known mouse x-coordinate
                self.last_mouse_x = event.pos[0]
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not self.game_started:
                    self.game_started = True  # Start the level on mouse click
                elif self.game_over or self.game_won:
                    self.reset_game()

    def draw_game_screen(self):
        self.screen.fill((0, 0, 0))  # Clear screen
        self.paddle.draw(self.screen)
        self.ball.draw(self.screen)
        for brick in self.bricks:
            brick.draw(self.screen)
        self.draw_score()
        self.draw_high_score()
        self.draw_level()  # Draw the current level
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
            self.wall_paddle_bounce_sound.play()
            self.normalize_ball_velocity()
        elif self.ball.position.x >= self.screen_width - self.ball.radius:
            self.ball.velocity.x *= -1
            self.ball.position.x = self.screen_width - self.ball.radius  # Nudge the ball away from the right edge
            self.wall_paddle_bounce_sound.play()
            self.normalize_ball_velocity()

        if self.ball.position.y <= self.ball.radius:
            self.ball.velocity.y *= -1
            self.ball.position.y = self.ball.radius  # Nudge the ball away from the top edge
            self.wall_paddle_bounce_sound.play()
            self.normalize_ball_velocity()

        # Ball and paddle
        if self.paddle_collision():
            # Calculate the offset from the center of the paddle
            offset = (self.ball.position.x - self.paddle.position.x) / self.paddle.width - 0.5
            self.adjust_ball_velocity_for_paddle_collision(offset)
            self.wall_paddle_bounce_sound.play()

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
        
        self.play_brick_sound(brick.color)
        
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
            if self.level < 5:
                self.level += 1
                self.reset_game()
            else:
                self.game_won = True  # Player wins the game after beating level 5

    def reset_game(self, initial=False):
        if not initial:
            if self.game_over or self.game_won:
                self.level = 1
                self.score = 0
            self.game_started = False  # Wait for player's action to start the level
            self.game_over = False
            self.game_won = False

        self.position_ball_on_paddle()
        self.ball.velocity = Vector2(self.ball.speed, -self.ball.speed)

        self.load_level(self.level)  # Load the current level

    def position_ball_on_paddle(self):
        paddle_top = self.screen_height - self.paddle.height - self.ball.radius
        self.ball.position = Vector2(self.paddle.position.x + self.paddle.width / 2, paddle_top)
    
    def update_game_state(self):
        if self.game_started and not (self.game_over or self.game_won):
            # Use pygame.mouse.get_pos() to get the current mouse position
            mouse_x, _ = pygame.mouse.get_pos()

            # Limit the paddle's movement to within the screen width
            if 0 <= mouse_x <= self.screen_width:
                self.paddle.move(mouse_x, self.screen_width)

            self.ball.move()
            self.check_collisions()
            self.check_win_condition()
            if self.ball.position.y - self.ball.radius > self.screen_height:
                self.game_over = True

    def draw_score(self):
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (5, 5))
        
    def draw_high_score(self):
        high_score_text = f"High Score: {self.high_score}"
        high_score_surface = self.font.render(high_score_text, True, (255, 255, 255))

        # Calculate the x-coordinate for centered text
        high_score_x = (self.screen_width - high_score_surface.get_width()) // 2
        high_score_y = 10  # A small offset from the top of the screen

        self.screen.blit(high_score_surface, (high_score_x, high_score_y))
        
    def draw_level(self):
        level_text = f"Level: {self.level}"
        level_surface = self.font.render(level_text, True, (255, 255, 255))
        self.screen.blit(level_surface, (self.screen_width - 100, 10))

    def draw_game_over_screen(self):
        self.display_centered_text("GAME OVER", self.screen_height // 2 - 30)
        self.display_centered_text(f"Final Score: {self.score}", self.screen_height // 2)
        self.display_centered_text("Click to Restart", self.screen_height // 2 + 30)
        self.update_high_score()

    def draw_win_screen(self):
        self.display_centered_text("Congratulations, you win!", self.screen_height // 2 - 30)
        self.display_centered_text(f"Final Score: {self.score}", center_y)
        self.display_centered_text("Click to Restart", center_y + 30)

        pygame.display.flip()

    def draw_start_screen(self):
        self.screen.fill((0, 0, 0))  # Clear screen

        # Load the logo image from the 'assets' folder
        logo_image_path = 'assets/logo.png'
        logo_image = pygame.image.load(logo_image_path)

        # Resize the logo to fill the entire game screen
        logo_image = pygame.transform.scale(logo_image, (self.screen_width, self.screen_height))

        # Display the resized logo image
        self.screen.blit(logo_image, (0, 0))

        # Position the "Click to Start" text at the bottom of the screen
        self.display_centered_text("Click to Start", self.screen_height - 30)
        pygame.display.flip()
        
    def display_centered_text(self, text, y_offset):
        text_surface = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, y_offset))
        self.screen.blit(text_surface, text_rect)

# Main execution
if __name__ == "__main__":
    game_manager = GameManager()
    game_manager.run()