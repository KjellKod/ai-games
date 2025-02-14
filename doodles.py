
import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH = 800
HEIGHT = 600
CELL_SIZE = 40

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ghost Spiral")
clock = pygame.time.Clock()

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.speed = 5
        self.size = 20
        self.color = WHITE

    def move(self, dx, dy):
        self.x = max(0, min(WIDTH - self.size, self.x + dx * self.speed))
        self.y = max(0, min(HEIGHT - self.size, self.y + dy * self.speed))

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))

class Ghost:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = 1
        self.size = 20
        self.color = WHITE
        self.angle = 0
        self.spiral_speed = 0.02

    def update(self, player):
        # Spiral movement towards player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.hypot(dx, dy)
        
        if distance > 0:
            self.angle += self.spiral_speed
            self.x += math.cos(self.angle) * self.speed + dx/distance * self.speed
            self.y += math.sin(self.angle) * self.speed + dy/distance * self.speed

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

class RedGhost:
    def __init__(self):
        self.x = WIDTH
        self.y = 50
        self.speed = 5
        self.size = 30
        self.color = RED

    def update(self):
        self.x -= self.speed
        if self.x < -self.size:
            self.x = WIDTH

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

class Laser:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.speed = 10
        self.size = 5

    def update(self):
        self.y -= self.speed

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size*2))

# Initialize game objects
player = Player()
ghosts = [Ghost() for _ in range(5)]
red_ghost = None
lasers = []
game_over = False
speed_increase_timer = 0

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        if not game_over:
            # Shooting controls
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:  # Blue laser
                    lasers.append(Laser(player.x + player.size//2, player.y, BLUE))
                if event.key == pygame.K_s and red_ghost:  # Red laser
                    lasers.append(Laser(player.x + player.size//2, player.y, RED))

    if not game_over:
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move(-1, 0)
        if keys[pygame.K_RIGHT]:
            player.move(1, 0)
        if keys[pygame.K_UP]:
            player.move(0, -1)
        if keys[pygame.K_DOWN]:
            player.move(0, 1)

        # Update game objects
        for ghost in ghosts:
            ghost.update(player)
        
        if red_ghost:
            red_ghost.update()

        # Update lasers
        for laser in lasers:
            laser.update()
            # Remove lasers that go off screen
            if laser.y < -laser.size*2:
                lasers.remove(laser)

        # Check collisions
        for ghost in ghosts[:]:
            # Check collision with player
            if (player.x < ghost.x + ghost.size and
                player.x + player.size > ghost.x and
                player.y < ghost.y + ghost.size and
                player.y + player.size > ghost.y):
                game_over = True
            
# Check collision with lasers
            for laser in lasers[:]:
                if (laser.x < ghost.x + ghost.size and
                    laser.x + laser.size > ghost.x and
                    laser.y < ghost.y + ghost.size and
                    laser.y + laser.size*2 > ghost.y):
                    ghosts.remove(ghost)
                    lasers.remove(laser)
                    break

        # Check collision with red ghost
        if red_ghost:
            # Player collision
            if (player.x < red_ghost.x + red_ghost.size and
                player.x + player.size > red_ghost.x and
                player.y < red_ghost.y + red_ghost.size and
                player.y + player.size > red_ghost.y):
                game_over = True
            
            # Laser collision
            for laser in lasers[:]:
                if (laser.x < red_ghost.x + red_ghost.size and
                    laser.x + laser.size > red_ghost.x and
                    laser.y < red_ghost.y + red_ghost.size and
                    laser.y + laser.size*2 > red_ghost.y):
                    if laser.color == RED:  # Only red lasers can destroy red ghost
                        red_ghost = None
                        lasers.remove(laser)
                        break

        # Increase ghost speed over time
        speed_increase_timer += 1
        if speed_increase_timer >= 600:  # Every 10 seconds
            speed_increase_timer = 0
            for ghost in ghosts:
                ghost.speed += 0.5

        # Spawn red ghost every 30 seconds
        if pygame.time.get_ticks() % 30000 == 0:
            red_ghost = RedGhost()

    # Drawing
    screen.fill(BLACK)
    player.draw()
    for ghost in ghosts:
        ghost.draw()
    if red_ghost:
        red_ghost.draw()
    for laser in lasers:
        laser.draw()

    # Draw game over screen
    if game_over:
        font = pygame.font.SysFont(None, 72)
        text = font.render('Game Over!', True, RED)
        text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(text, text_rect)

    pygame.display.flip()
    clock.tick(60)


