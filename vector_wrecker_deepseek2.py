import pygame
import math
import sys
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TRACK_WIDTH = 60
CAR_LENGTH = 20
CAR_WIDTH = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Game settings
FPS = 60
BASE_SPEED = 1.0
SPEED_MULTIPLIER = 10

class Car:
    def __init__(self):
        self.position = [400, 300]
        self.velocity = [1.0, 0.0]
        self.rotation = 0
        self.speed = BASE_SPEED

    def get_points(self):
        angle = math.radians(self.rotation)
        front = [
            self.position[0] + math.cos(angle) * CAR_LENGTH,
            self.position[1] - math.sin(angle) * CAR_LENGTH
        ]
        back_left = [
            self.position[0] - math.cos(angle) * CAR_LENGTH/2 - math.sin(angle) * CAR_WIDTH/2,
            self.position[1] + math.sin(angle) * CAR_LENGTH/2 - math.cos(angle) * CAR_WIDTH/2
        ]
        back_right = [
            self.position[0] - math.cos(angle) * CAR_LENGTH/2 + math.sin(angle) * CAR_WIDTH/2,
            self.position[1] + math.sin(angle) * CAR_LENGTH/2 + math.cos(angle) * CAR_WIDTH/2
        ]
        return [front, back_left, back_right]

class Track:
    def __init__(self):
        # Create a large oval track
        self.width = TRACK_WIDTH
        self.boundaries = []
        self.start_line = None
        
        # Outer boundary
        outer_points = []
        # Top straight
        for x in range(200, 1400, 10):
            outer_points.append((x, 100))
        # Right curve
        for angle in range(270, 360, 5):
            x = 1400 + 500 * math.cos(math.radians(angle))
            y = 300 + 500 * math.sin(math.radians(angle))
            outer_points.append((x, y))
        # Bottom straight
        for x in range(1400, 200, -10):
            outer_points.append((x, 500))
        # Left curve
        for angle in range(0, 90, 5):
            x = 200 + 500 * math.cos(math.radians(angle))
            y = 300 + 500 * math.sin(math.radians(angle))
            outer_points.append((x, y))
        
        # Inner boundary (offset by track width)
        inner_points = []
        for x, y in outer_points:
            dx = x - 800
            dy = y - 300
            dist = math.hypot(dx, dy)
            if dist == 0:
                inner_points.append((x, y))
            else:
                scale = (dist - TRACK_WIDTH) / dist
                inner_points.append((800 + dx * scale, 300 + dy * scale))
        
        self.boundaries = outer_points + inner_points[::-1]
        self.start_line = ((200, 300), (200 + TRACK_WIDTH, 300))

class GameState:
    def __init__(self):
        self.car = Car()
        self.track = Track()
        self.current_options = []
        self.selected_option = 0
        self.game_active = True
        self.victory = False
        self.generate_movement_options()

    def generate_movement_options(self):
        angle = math.radians(self.car.rotation)
        base_vector = [math.cos(angle), -math.sin(angle)]
        
        # Generate 5 options in front of the car
        self.current_options = []
        for i in range(-2, 3):
            option_angle = angle + math.radians(i * 15)
            dx = math.cos(option_angle) * self.car.speed
            dy = -math.sin(option_angle) * self.car.speed
            self.current_options.append((dx, dy))

    def update(self):
        if not self.game_active:
            return
        
        # Update car position
        self.car.position[0] += self.car.velocity[0]
        self.car.position[1] += self.car.velocity[1]
        
        # Update rotation
        if self.car.velocity[0] != 0 or self.car.velocity[1] != 0:
            self.car.rotation = math.degrees(math.atan2(-self.car.velocity[1], self.car.velocity[0]))
        
        # Check collisions
        if self.check_collision():
            self.game_active = False
        
        # Check victory condition
        if self.check_victory():
            self.victory = True
            self.game_active = False

    def check_collision(self):
        car_points = self.car.get_points()
        for point in car_points:
            if not self.point_in_track(point):
                return True
        return False

    def point_in_track(self, point):
        # Simple point-in-polygon check
        x, y = point
        n = len(self.track.boundaries)
        inside = False
        for i in range(n):
            x1, y1 = self.track.boundaries[i]
            x2, y2 = self.track.boundaries[(i+1)%n]
            if y > min(y1, y2):
                if y <= max(y1, y2):
                    if x <= max(x1, x2):
                        if y1 != y2:
                            xinters = (y-y1)*(x2-x1)/(y2-y1)+x1
                        if y1 == y2 or x <= xinters:
                            inside = not inside
        return inside

    def check_victory(self):
        # Check if car has crossed start line
        car_front = self.car.get_points()[0]
        start_line = self.track.start_line
        return self.lines_intersect(start_line[0], start_line[1], 
                                  self.car.position, car_front)

    def lines_intersect(self, a1, a2, b1, b2):
        def ccw(A,B,C):
            return (C[1]-A[1])*(B[0]-A[0]) > (B[1]-A[1])*(C[0]-A[0])
        return ccw(a1,b1,b2) != ccw(a2,b1,b2) and ccw(a1,a2,b1) != ccw(a1,a2,b2)

def draw_track(screen, track):
    pygame.draw.polygon(screen, GRAY, track.boundaries)
    pygame.draw.lines(screen, WHITE, True, track.boundaries, 2)

def draw_car(screen, car):
    points = car.get_points()
    pygame.draw.polygon(screen, GREEN, points)

def draw_ui(screen, game_state):
    # Draw speed display
    font = pygame.font.SysFont(None, 30)
    speed_text = font.render(f"Speed: {game_state.car.speed:.2f}", True, WHITE)
    screen.blit(speed_text, (10, 10))
    
    # Draw game over/victory screen
    if not game_state.game_active:
        font = pygame.font.SysFont(None, 60)
        if game_state.victory:
            text = font.render("Lap Complete!", True, YELLOW)
        else:
            text = font.render("Game Over", True, RED)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        text = font.render("Press R to restart", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 + 10))

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Vector Wrecker")
    clock = pygame.time.Clock()
    
    game_state = GameState()
    
    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                
                if game_state.game_active:
                    if event.key == pygame.K_SPACE:
                        # Apply selected movement
                        game_state.car.velocity = list(game_state.current_options[game_state.selected_option])
                        game_state.car.speed = math.hypot(*game_state.car.velocity)
                        game_state.generate_movement_options()
                    
                    # Cycle through options with arrow keys
                    if event.key == pygame.K_LEFT:
                        game_state.selected_option = (game_state.selected_option - 1) % 5
                    if event.key == pygame.K_RIGHT:
                        game_state.selected_option = (game_state.selected_option + 1) % 5
                    if event.key == pygame.K_UP:
                        game_state.car.speed += 0.1
                        game_state.generate_movement_options()
                    if event.key == pygame.K_DOWN:
                        game_state.car.speed = max(0.1, game_state.car.speed - 0.1)
                        game_state.generate_movement_options()
                
                if event.key == pygame.K_r:
                    # Restart game
                    game_state = GameState()
        
        # Update game state
        game_state.update()
        
        # Draw everything
        screen.fill(BLACK)
        draw_track(screen, game_state.track)
        draw_car(screen, game_state.car)
        
        # Draw movement options
        if game_state.game_active:
            for i, option in enumerate(game_state.current_options):
                color = YELLOW if i == game_state.selected_option else WHITE
                start_pos = game_state.car.position
                end_pos = [
                    start_pos[0] + option[0] * SPEED_MULTIPLIER,
                    start_pos[1] + option[1] * SPEED_MULTIPLIER
                ]
                pygame.draw.line(screen, color, start_pos, end_pos, 2)
                pygame.draw.circle(screen, color, [int(x) for x in end_pos], 4)
        
        draw_ui(screen, game_state)
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
