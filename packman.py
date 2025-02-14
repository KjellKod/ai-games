import pygame
import sys
import random

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
GREEN = (0, 255, 0)

# Corrected maze layout (fixed central corridor)
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
    "# ############### #",
    "#     #     #     #",  # Row 9
    "# ### # ### # ### #",
    "# ### # ### # ### #",
    "#.................#",
    "# ### ## # ## ### #",
    "# ### ## # ## ### #",
    "# ### ## # ## ### #",
    "#.................#",  # Row 17 - open corridor
    "###################",
]

def reset_game():
    global score, lives, dots, pacman, ghost, game_over
    score = 0
    lives = 3
    game_over = False
    
    # Reset dots
    for y in range(len(MAZE)):
        for x in range(len(MAZE[y])):
            dots[y][x] = MAZE[y][x] in ('.', ' ')
    
    # Reset characters with valid starting positions
    pacman.update({
        "grid_x": 9,  # Center of open corridor
        "grid_y": 17, # Row 17 (now open)
        "progress": 0,
        "direction": (0, 0),
        "next_dir": (0, 0)
    })
    ghost.update({
        "grid_x": 9,
        "grid_y": 5,
        "progress": 0,
        "direction": (0, 0)
    })

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man")
clock = pygame.time.Clock()

# Game state
score = 0
lives = 3
game_over = False

# Initialize dots
dots = []
for y, row in enumerate(MAZE):
    dot_row = []
    for x, char in enumerate(row):
        dot_row.append(char in ('.', ' '))
    dots.append(dot_row)

# Initialize Pac-Man with valid starting position
pacman = {
    "grid_x": 9,
    "grid_y": 17,
    "progress": 0,
    "direction": (0, 0),
    "next_dir": (0, 0),
    "speed": 3
}

# Initialize Ghost
ghost = {
    "grid_x": 9,
    "grid_y": 5,
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
            new_x = character["grid_x"] + character["direction"][0]
            new_y = character["grid_y"] + character["direction"][1]
            
            # Check if new position is valid before moving
            if 0 <= new_x < len(maze[0]) and 0 <= new_y < len(maze):
                if maze[new_y][new_x] != "#":
                    character["grid_x"] = new_x
                    character["grid_y"] = new_y
                    character["progress"] = overflow
                else:
                    character["direction"] = (0, 0)
                    character["progress"] = 0
            else:
                # Handle tunnel wrap-around
                if new_x < 0:
                    character["grid_x"] = len(maze[0]) - 1
                elif new_x >= len(maze[0]):
                    character["grid_x"] = 0
                else:
                    character["direction"] = (0, 0)
                    character["progress"] = 0

def handle_pacman_input():
    keys = pygame.key.get_pressed()
    new_dir = None
    
    if keys[pygame.K_LEFT]:
        new_dir = (-1, 0)
    elif keys[pygame.K_RIGHT]:
        new_dir = (1, 0)
    elif keys[pygame.K_UP]:
        new_dir = (0, -1)
    elif keys[pygame.K_DOWN]:
        new_dir = (0, 1)
    
    if keys[pygame.K_r] and game_over:
        reset_game()

    if new_dir and not game_over:
        # Check if we can change direction immediately
        if pacman["progress"] == 0:
            next_x = pacman["grid_x"] + new_dir[0]
            next_y = pacman["grid_y"] + new_dir[1]
            if 0 <= next_x < len(MAZE[0]) and 0 <= next_y < len(MAZE):
                if MAZE[next_y][next_x] != "#":
                    pacman["direction"] = new_dir
        else:
            # Queue direction change for next intersection
            pacman["next_dir"] = new_dir

def move_ghost():
    if game_over:
        return
    
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

def check_collisions():
    global score, lives, game_over
    
    if game_over:
        return
    
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
            game_over = True
        else:
            # Reset positions
            pacman.update({
                "grid_x": 9, "grid_y": 17,
                "progress": 0, "direction": (0, 0),
                "next_dir": (0, 0)
            })
            ghost.update({
                "grid_x": 9, "grid_y": 5,
                "progress": 0, "direction": (0, 0)
            })

def draw():
    screen.fill(BLACK)
    
    # Draw maze
    for y in range(len(MAZE)):
        for x in range(len(MAZE[y])):
            if MAZE[y][x] == "#":
                pygame.draw.rect(screen, BLUE, 
                               (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            if dots[y][x]:
                center = (x*CELL_SIZE + CELL_SIZE//2, y*CELL_SIZE + CELL_SIZE//2)
                pygame.draw.circle(screen, WHITE, center, 3)
    
    # Draw Pac-Man
    if not game_over:
        px = (pacman["grid_x"] + pacman["direction"][0] * pacman["progress"]) * CELL_SIZE
        py = (pacman["grid_y"] + pacman["direction"][1] * pacman["progress"]) * CELL_SIZE
        pygame.draw.circle(screen, YELLOW, (px + CELL_SIZE//2, py + CELL_SIZE//2), CELL_SIZE//2 - 2)
    
    # Draw Ghost
    gx = (ghost["grid_x"] + ghost["direction"][0] * ghost["progress"]) * CELL_SIZE
    gy = (ghost["grid_y"] + ghost["direction"][1] * ghost["progress"]) * CELL_SIZE
    pygame.draw.rect(screen, RED, (gx, gy, CELL_SIZE, CELL_SIZE))
    
    # Draw UI
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(score_text, (10, HEIGHT - 50))
    screen.blit(lives_text, (WIDTH - 120, HEIGHT - 50))
    
    # Draw game over screen
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        go_font = pygame.font.Font(None, 72)
        go_text = go_font.render("GAME OVER", True, RED)
        restart_text = font.render("Press R to restart", True, GREEN)
        
        screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 20))
    
    pygame.display.flip()

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    handle_pacman_input()
    
    if not game_over:
        move_character(pacman, MAZE)
        move_ghost()
        check_collisions()
        
        # Handle queued direction changes
        if pacman["next_dir"] != (0, 0) and pacman["progress"] == 0:
            next_x = pacman["grid_x"] + pacman["next_dir"][0]
            next_y = pacman["grid_y"] + pacman["next_dir"][1]
            if 0 <= next_x < len(MAZE[0]) and 0 <= next_y < len(MAZE):
                if MAZE[next_y][next_x] != "#":
                    pacman["direction"] = pacman["next_dir"]
                    pacman["next_dir"] = (0, 0)
    
    draw()
    clock.tick(FPS)
