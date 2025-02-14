import pygame
import math
import random

# Initialize pygame
pygame.init()

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (50, 50, 50)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Define window dimensions
WIDTH, HEIGHT = 800, 600

# Create the game window
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vector Wrecker")

# Set up the clock
clock = pygame.time.Clock()
FPS = 60


class Car:
    def __init__(self):
        self.position = [100, HEIGHT // 2]  # Starting position
        self.velocity = [1, 0]  # Initial velocity vector
        self.rotation = 0  # Degrees

    def update_position(self, new_velocity):
        self.velocity[0] += new_velocity[0]
        self.velocity[1] += new_velocity[1]
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
        self.rotation = math.degrees(math.atan2(-self.velocity[1], self.velocity[0]))


class Track:
    def __init__(self):
        self.width = 60
        self.boundaries = self.generate_track()
        self.start_line = [(100, HEIGHT // 2 - self.width // 2), (100, HEIGHT // 2 + self.width // 2)]

    def generate_track(self):
        # Generate a simple track with a straight section and random curves
        points = [(100, HEIGHT // 2)]
        for _ in range(10):
            x = points[-1][0] + random.randint(50, 150)
            y = points[-1][1] + random.randint(-50, 50)
            points.append((x, y))
        return points


class GameState:
    def __init__(self):
        self.car = Car()
        self.track = Track()
        self.current_options = []
        self.selected_option = 0
        self.game_active = True
        self.victory = False

    def calculate_options(self):
        # Calculate 5 possible movement options
        options = [
            (0, 0),  # Maintain current
            (1, 0),  # Forward
            (1, -1),  # Forward-left
            (1, 1),  # Forward-right
            (-1, 0),  # Backward
        ]
        self.current_options = options

    def check_collision(self):
        # Simple collision check with track boundaries
        for point in self.track.boundaries:
            distance = math.hypot(self.car.position[0] - point[0], self.car.position[1] - point[1])
            if distance > self.track.width // 2:
                self.game_active = False

    def check_victory(self):
        # Check if the car has crossed the start line
        if self.car.position[0] > self.track.start_line[0][0] and abs(self.car.position[1] - HEIGHT // 2) < 10:
            self.victory = True
            self.game_active = False


def draw_track(track):
    # Draw track boundaries
    for i in range(len(track.boundaries) - 1):
        pygame.draw.line(window, WHITE, track.boundaries[i], track.boundaries[i + 1], 2)
    # Draw inner area
    pygame.draw.polygon(window, DARK_GRAY, track.boundaries)


def draw_car(car):
    # Draw the car as a triangle
    angle_rad = math.radians(car.rotation)
    points = [
        (car.position[0] + 20 * math.cos(angle_rad), car.position[1] - 20 * math.sin(angle_rad)),
        (car.position[0] + 10 * math.cos(angle_rad + math.pi / 2), car.position[1] - 10 * math.sin(angle_rad + math.pi / 2)),
        (car.position[0] + 10 * math.cos(angle_rad - math.pi / 2), car.position[1] - 10 * math.sin(angle_rad - math.pi / 2)),
    ]
    pygame.draw.polygon(window, GREEN, points)


def draw_ui(game_state):
    # Draw speed display
    speed = math.hypot(game_state.car.velocity[0], game_state.car.velocity[1])
    speed_text = pygame.font.SysFont("sans-serif", 20).render(f"Speed: {speed:.2f}", True, WHITE)
    window.blit(speed_text, (10, 10))

    # Draw movement options
    for i, option in enumerate(game_state.current_options):
        color = YELLOW if i == game_state.selected_option else WHITE
        pygame.draw.circle(window, color, (100 + i * 50, HEIGHT - 50), 4)
        pygame.draw.line(window, color, (100 + i * 50, HEIGHT - 50), game_state.car.position, 1)

    # Draw current vector
    pygame.draw.line(window, RED, game_state.car.position, (
        game_state.car.position[0] + game_state.car.velocity[0] * 10,
        game_state.car.position[1] + game_state.car.velocity[1] * 10,
    ), 2)

    # Draw game over or victory screen
    if not game_state.game_active:
        message = "Lap Complete!" if game_state.victory else "Game Over"
        message_text = pygame.font.SysFont("sans-serif", 40).render(message, True, WHITE)
        window.blit(message_text, (WIDTH // 2 - 100, HEIGHT // 2 - 20))
        restart_text = pygame.font.SysFont("sans-serif", 20).render("Press R to restart", True, WHITE)
        window.blit(restart_text, (WIDTH // 2 - 80, HEIGHT // 2 + 20))


def main():
    game_state = GameState()
    running = True

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r and not game_state.game_active:
                    game_state = GameState()  # Restart game
                if game_state.game_active:
                    if event.key == pygame.K_SPACE:
                        game_state.car.update_position(game_state.current_options[game_state.selected_option])
                        game_state.check_collision()
                        game_state.check_victory()
                    if event.key == pygame.K_LEFT:
                        game_state.selected_option = (game_state.selected_option - 1) % 5
                    if event.key == pygame.K_RIGHT:
                        game_state.selected_option = (game_state.selected_option + 1) % 5

        # Update game state
        if game_state.game_active:
            game_state.calculate_options()

        # Draw everything
        window.fill(BLACK)
        draw_track(game_state.track)
        draw_car(game_state.car)
        draw_ui(game_state)
        pygame.display.update()

        # Maintain FPS
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
