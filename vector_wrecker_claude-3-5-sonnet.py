import pygame
import sys
import math
from pygame import Vector2
from typing import List, Tuple
import random

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
DARK_GRAY = (50, 50, 50)
YELLOW = (255, 255, 0)

# Game Constants
TRACK_WIDTH = 60
CAR_LENGTH = 20
CAR_WIDTH = 10

class Car:
    def __init__(self, pos: Vector2):
        self.position = Vector2(pos)
        self.velocity = Vector2(1, 0)  # Initial velocity: 1 unit right
        self.rotation = 0  # Degrees

    def draw(self, screen):
        # Draw car as triangle
        points = self._get_triangle_points()
        pygame.draw.polygon(screen, GREEN, points)
        
        # Draw velocity vector
        end_pos = self.position + self.velocity * 10
        pygame.draw.line(screen, RED, self.position, end_pos, 2)

    def _get_triangle_points(self) -> List[Tuple[float, float]]:
        # Calculate triangle points based on position and rotation
        front = self.position + Vector2(CAR_LENGTH/2, 0).rotate(self.rotation)
        back_left = self.position + Vector2(-CAR_LENGTH/2, CAR_WIDTH/2).rotate(self.rotation)
        back_right = self.position + Vector2(-CAR_LENGTH/2, -CAR_WIDTH/2).rotate(self.rotation)
        return [front, back_left, back_right]

    def get_move_options(self) -> List[Vector2]:
        # Return 5 possible move vectors
        return [
            self.velocity,  # maintain current
            self.velocity + Vector2(1, 0),  # add forward
            self.velocity + Vector2(1, -1),  # forward-left
            self.velocity + Vector2(1, 1),  # forward-right
            self.velocity + Vector2(-1, 0)  # backward
        ]

class Track:
    def __init__(self):
        self.boundaries = self._generate_track()
        self.width = TRACK_WIDTH

    def _generate_track(self) -> List[Vector2]:
        # Temporary simple oval track for testing
        points = []
        center = Vector2(WINDOW_WIDTH/2, WINDOW_HEIGHT/2)
        for angle in range(0, 360, 10):
            rad = math.radians(angle)
            x = center.x + math.cos(rad) * 200
            y = center.y + math.sin(rad) * 150
            points.append(Vector2(x, y))
        return points

    def draw(self, screen):
        # Draw track boundaries
        if len(self.boundaries) > 1:
            pygame.draw.lines(screen, WHITE, True, self.boundaries, 2)
            # Draw inner track
            pygame.draw.lines(screen, DARK_GRAY, True, self.boundaries, TRACK_WIDTH)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Vector Wrecker")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize game objects
        self.track = Track()
        starting_pos = Vector2(WINDOW_WIDTH/2, WINDOW_HEIGHT-100)
        self.car = Car(starting_pos)
        
        self.selected_option = 0
        self.game_active = True
        self.victory = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % 5
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % 5
                elif event.key == pygame.K_SPACE and self.game_active:
                    self._confirm_move()

    def _confirm_move(self):
        options = self.car.get_move_options()
        self.car.velocity = options[self.selected_option]
        self.car.position += self.car.velocity * 10
        self.car.rotation = math.degrees(math.atan2(self.car.velocity.y, self.car.velocity.x))

    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw track
        self.track.draw(self.screen)
        
        # Draw car
        self.car.draw(self.screen)
        
        # Draw move options
        options = self.car.get_move_options()
        for i, option in enumerate(options):
            end_pos = self.car.position + option * 10
            color = YELLOW if i == self.selected_option else WHITE
            pygame.draw.circle(self.screen, color, end_pos, 4)
            pygame.draw.line(self.screen, color, self.car.position, end_pos, 1)

        # Draw speed
        speed_text = f"Speed: {self.car.velocity.length():.2f}"
        font = pygame.font.Font(None, 36)
        text_surface = font.render(speed_text, True, WHITE)
        self.screen.blit(text_surface, (10, 10))

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()
