import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Game constants
CELL_SIZE = 30
MAZE_WIDTH = 19
MAZE_HEIGHT = 21
WIDTH = CELL_SIZE * MAZE_WIDTH
HEIGHT = CELL_SIZE * MAZE_HEIGHT + 60
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Maze layout
MAZE = [
    "###################",
    "#........#........#",
    "# ### ## # ## ### #",
    "# ### ## # ## ### #",
    "# ### ## # ## ### #",
    "#.................#",
    "# ### # ### # ### #",
    "# ### # ### # ### #",
    "#     #     #     #",
    "###################",
    "#     #     #     #",
    "# ### # ### # ### #",
    "# ### # ### # ### #",
    "#.................#",
    "# ### ## # ## ### #",
    "# ### ## # ## ### #",
    "# ### ## # ## ### #",
    "#........#........#",
    "###################",
]

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man")
clock = pygame.time.Clock()

# Game state
score = 0
lives = 3

# Initialize dots
dots = []
for y, row in enumerate(MAZE):
    dot_row = []
    for x, char in enumerate(row):
        dot_row.append(char == '.')
    dots.append(dot_row)

def find_starting_position(maze):
    """Find a valid starting position for Pac-Man near the bottom of the maze."""
    # Start from bottom row (excluding the very last row which is usually a wall)
    for y in range(len(maze) - 2, 0, -1):
        # Look for a position in the middle third of the row
        start_x = len(maze[0]) // 3
        end_x = (len(maze[0]) * 2) // 3
        
        for x in range(start_x, end_x):
            # Check if position is valid (not a wall)
            if maze[y][x] != '#':
                # Check if there's space to move (at least one adjacent cell is free)
                adjacent_spaces = [
                    (x + 1, y), (x - 1, y),  # Left and right
                    (x, y + 1), (x, y - 1)   # Up and down
                ]
                for adj_x, adj_y in adjacent_spaces:
                    if (0 <= adj_x < len(maze[0]) and 
                        0 <= adj_y < len(maze) and 
                        maze[adj_y][adj_x] != '#'):
                        return x, y
    
    # Fallback to center position if no suitable position found
    return len(maze[0]) // 2, len(maze) // 2


# Initialize Pac-Man with automatic position
start_x, start_y = find_starting_position(MAZE)
pacman = {
    "grid_x": start_x,
    "grid_y": start_y,
    "progress": 0,
    "direction": (0, 0),
    "next_dir": (0, 0),
    "speed": 3
}

# Initialize Ghost (modify these values too)
ghost = {
    "grid_x": 9,  # Center of maze
    "grid_y": 9,  # Middle of maze
    "progress": 0,
    "direction": (0, 0),
    "speed": 2,
    "next_dir": (0, 0)
}

def move_character(character, maze):
    if character["direction"] != (0, 0):
        character["progress"] += character["speed"] / CELL_SIZE
        
        if character["progress"] >= 1:
            overflow = character["progress"] - 1
            character["grid_x"] += character["direction"][0]
            character["grid_y"] += character["direction"][1]
            character["progress"] = overflow
            
            # Handle tunnel wrap-around
            if character["grid_x"] < 0:
                character["grid_x"] = len(maze[0]) - 1
            elif character["grid_x"] >= len(maze[0]):
                character["grid_x"] = 0

            # Check next direction
            next_x = character["grid_x"] + character["direction"][0]
            next_y = character["grid_y"] + character["direction"][1]
            
            if not (0 <= next_x < len(maze[0]) and 0 <= next_y < len(maze)) or \
               maze[next_y][next_x] == "#":
                character["direction"] = (0, 0)

def handle_pacman_input():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.KEYDOWN:
            new_dir = None
            if event.key == pygame.K_LEFT:
                new_dir = (-1, 0)
            elif event.key == pygame.K_RIGHT:
                new_dir = (1, 0)
            elif event.key == pygame.K_UP:
                new_dir = (0, -1)
            elif event.key == pygame.K_DOWN:
                new_dir = (0, 1)
            
            if new_dir:
                next_x = pacman["grid_x"] + new_dir[0]
                next_y = pacman["grid_y"] + new_dir[1]
                
                if 0 <= next_x < len(MAZE[0]) and 0 <= next_y < len(MAZE):
                    if MAZE[next_y][next_x] != "#":
                        if pacman["progress"] == 0:
                            pacman["direction"] = new_dir
                        else:
                            pacman["next_dir"] = new_dir

def move_ghost():
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    
    if ghost["progress"] == 0:
        possible_dirs = []
        current_dir = ghost["direction"]
        
        for dx, dy in directions:
            new_x = ghost["grid_x"] + dx
            new_y = ghost["grid_y"] + dy
            
            if 0 <= new_x < len(MAZE[0]) and 0 <= new_y < len(MAZE):
                if MAZE[new_y][new_x] != "#" and (dx, dy) != (-current_dir[0], -current_dir[1]):
                    possible_dirs.append((dx, dy))
        
        if possible_dirs:
            ghost["direction"] = random.choice(possible_dirs)
        else:
            ghost["direction"] = (0, 0)
    
    move_character(ghost, MAZE)

def find_starting_position(maze):
    """Find a valid starting position for Pac-Man near the bottom of the maze."""
    # Start from bottom row (excluding the very last row which is usually a wall)
    for y in range(len(maze) - 2, 0, -1):
        # Look for a position in the middle third of the row
        start_x = len(maze[0]) // 3
        end_x = (len(maze[0]) * 2) // 3
        
        for x in range(start_x, end_x):
            # Check if position is valid (not a wall)
            if maze[y][x] != '#':
                # Check if there's space to move (at least one adjacent cell is free)
                adjacent_spaces = [
                    (x + 1, y), (x - 1, y),  # Left and right
                    (x, y + 1), (x, y - 1)   # Up and down
                ]
                for adj_x, adj_y in adjacent_spaces:
                    if (0 <= adj_x < len(maze[0]) and 
                        0 <= adj_y < len(maze) and 
                        maze[adj_y][adj_x] != '#'):
                        return x, y
    
    # Fallback to center position if no suitable position found
    return len(maze[0]) // 2, len(maze) // 2

def check_collisions():
    global score, lives
    
    # Check dot collection
    px = pacman["grid_x"]
    py = pacman["grid_y"]
    if dots[py][px]:
        dots[py][px] = False
        score += 10
    
    # Ghost collision
    pac_rect = pygame.Rect(
        (pacman["grid_x"] + pacman["direction"][0] * pacman["progress"]) * CELL_SIZE,
        (pacman["grid_y"] + pacman["direction"][1] * pacman["progress"]) * CELL_SIZE,
        CELL_SIZE, CELL_SIZE
    )
    
    ghost_rect = pygame.Rect(
        (ghost["grid_x"] + ghost["direction"][0] * ghost["progress"]) * CELL_SIZE,
        (ghost["grid_y"] + ghost["direction"][1] * ghost["progress"]) * CELL_SIZE,
        CELL_SIZE, CELL_SIZE
    )
    
    if pac_rect.colliderect(ghost_rect):
        lives -= 1
        if lives <= 0:
            pygame.quit()
            sys.exit()
        else:
            # Reset positions using the same function
            start_x, start_y = find_starting_position(MAZE)
            pacman.update({
                "grid_x": start_x, "grid_y": start_y,
                "progress": 0, "direction": (0, 0),
                "next_dir": (0, 0)
            })
            ghost.update({
                "grid_x": 9, "grid_y": 9,  # Could also make this dynamic
                "progress": 0, "direction": (0, 0)
            })

# Add these new constants
PACMAN_MOUTH_SPEED = 8  # Controls mouth animation speed
PACMAN_START_ANGLE = 20  # Mouth opening angle in degrees

# Add this new state variable after the game state section
pacman_mouth_angle = 0
pacman_mouth_opening = True

# Replace the handle_pacman_input function with this improved version
def handle_pacman_input():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.KEYDOWN:
            new_dir = None
            if event.key == pygame.K_LEFT:
                new_dir = (-1, 0)
            elif event.key == pygame.K_RIGHT:
                new_dir = (1, 0)
            elif event.key == pygame.K_UP:
                new_dir = (0, -1)
            elif event.key == pygame.K_DOWN:
                new_dir = (0, 1)
            
            if new_dir:
                # Always store the new direction as next_dir
                pacman["next_dir"] = new_dir
                
                # If Pac-Man is not moving, try to move immediately
                if pacman["direction"] == (0, 0):
                    next_x = pacman["grid_x"] + new_dir[0]
                    next_y = pacman["grid_y"] + new_dir[1]
                    if 0 <= next_x < len(MAZE[0]) and 0 <= next_y < len(MAZE) and MAZE[next_y][next_x] != "#":
                        pacman["direction"] = new_dir
                        pacman["next_dir"] = (0, 0)

def draw_pacman():
    global pacman_mouth_angle, pacman_mouth_opening
    
    # Calculate Pac-Man's position
    px = (pacman["grid_x"] + pacman["direction"][0] * pacman["progress"]) * CELL_SIZE
    py = (pacman["grid_y"] + pacman["direction"][1] * pacman["progress"]) * CELL_SIZE
    center = (px + CELL_SIZE//2, py + CELL_SIZE//2)
    
    # Update mouth animation
    if pacman["direction"] != (0, 0):
        if pacman_mouth_opening:
            pacman_mouth_angle += PACMAN_MOUTH_SPEED
            if pacman_mouth_angle >= PACMAN_START_ANGLE:
                pacman_mouth_opening = False
        else:
            pacman_mouth_angle -= PACMAN_MOUTH_SPEED
            if pacman_mouth_angle <= 0:
                pacman_mouth_opening = True
    
    # Calculate rotation based on direction
    rotation = 0
    if pacman["direction"] == (-1, 0):  # Left
        rotation = 180
    elif pacman["direction"] == (0, -1):  # Up
        rotation = 90
    elif pacman["direction"] == (0, 1):   # Down
        rotation = 270
    
    # Draw Pac-Man body
    pygame.draw.circle(screen, YELLOW, center, CELL_SIZE//2 - 2)
    
    # Draw Pac-Man mouth
    if pacman["direction"] != (0, 0):
        start_angle = rotation - pacman_mouth_angle
        end_angle = rotation + pacman_mouth_angle
        points = [center]
        
        # Ensure we generate at least 3 points for the polygon
        num_points = max(10, abs(int(end_angle - start_angle)))
        angle_step = (end_angle - start_angle) / num_points
        
        for i in range(num_points + 1):
            angle = math.radians(start_angle + (i * angle_step))
            x = center[0] + (CELL_SIZE//2 - 2) * math.cos(angle)
            y = center[1] - (CELL_SIZE//2 - 2) * math.sin(angle)
            points.append((x, y))
        
        # Only draw if we have enough points
        if len(points) > 2:
            pygame.draw.polygon(screen, BLACK, points)
            
# Update the draw function to use the new draw_pacman function
def draw():
    screen.fill(BLACK)
    
    # Draw maze and dots (unchanged)
    for y in range(len(MAZE)):
        for x in range(len(MAZE[y])):
            if MAZE[y][x] == "#":
                pygame.draw.rect(screen, BLUE, 
                               (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            if dots[y][x]:
                center = (x*CELL_SIZE + CELL_SIZE//2, y*CELL_SIZE + CELL_SIZE//2)
                pygame.draw.circle(screen, WHITE, center, 3)
    
    # Draw Pac-Man with the new function
    draw_pacman()
    
    # Draw Ghost (unchanged)
    gx = (ghost["grid_x"] + ghost["direction"][0] * ghost["progress"]) * CELL_SIZE
    gy = (ghost["grid_y"] + ghost["direction"][1] * ghost["progress"]) * CELL_SIZE
    pygame.draw.rect(screen, RED, (gx, gy, CELL_SIZE, CELL_SIZE))
    
    # Draw UI
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(score_text, (10, HEIGHT - 50))
    screen.blit(lives_text, (WIDTH - 120, HEIGHT - 50))
    
    pygame.display.flip()

# Main game loop
while True:
    # Handle input and movement
    handle_pacman_input()
    move_character(pacman, MAZE)
    move_ghost()
    check_collisions()
    
    # Handle Pac-Man's queued direction changes
    if pacman["next_dir"] != (0, 0):
        next_x = pacman["grid_x"] + pacman["next_dir"][0]
        next_y = pacman["grid_y"] + pacman["next_dir"][1]
        
        # Check if the next position is valid
        if 0 <= next_x < len(MAZE[0]) and 0 <= next_y < len(MAZE):
            if MAZE[next_y][next_x] != "#":
                # If Pac-Man is at a grid position or the new direction is perpendicular
                if (pacman["progress"] == 0 or 
                    (pacman["next_dir"][0] * pacman["direction"][0] == 0 and 
                     pacman["next_dir"][1] * pacman["direction"][1] == 0)):
                    pacman["direction"] = pacman["next_dir"]
                    pacman["next_dir"] = (0, 0)
    
    # Check win condition
    dots_remaining = any(any(row) for row in dots)
    if not dots_remaining:
        print("You win!")
        pygame.quit()
        sys.exit()
    
    # Draw everything
    draw()
    
    # Control game speed
    clock.tick(FPS)