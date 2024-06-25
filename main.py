# impoet libraries
import pygame
import sys
import random
import time

# Initialize Pygame
pygame.init()
pygame.font.init() 
font = pygame.font.SysFont('Arial', 30) 
pygame.display.set_caption("Platformer Game by Gabe")

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Classes
class GameObject:
    def __init__(self, x, y, width, height, colour):
        self.rect = pygame.Rect(x, y, width, height)
        self.colour = colour

    def draw(self, screen):
        pygame.draw.rect(screen, self.colour, self.rect)

class Obstacle(GameObject):
    def __init__(self, x, y, width, height, colour, speed):
        super().__init__(x, y, width, height, colour)
        self.speed = speed

    def move(self):
        self.rect.y += self.speed
        if self.rect.y < ground_y or self.rect.y > 0:
            # Create particles
            if random.randint(0, 1) == 0:  
                particles.append(Particle(self.rect.centerx + random.randint(-7, 7), self.rect.centery, self.colour, 30, 6, 0, random.uniform(-2, 2)))
        
    def update(self, screen):
        self.move()
        self.draw(screen)
        
class SidewaysObstacle(GameObject):
    def __init__(self, x, y, width, height, colour, speed_x):
        super().__init__(x, y, width, height, colour)
        self.speed_x = speed_x
 
    def move_sideways(self):
        self.rect.x += self.speed_x
        if self.rect.x < 0 or self.rect.x + self.rect.width > SCREEN_WIDTH:
            # Create particles
            for i in range(100):
                particles.append(Particle(self.rect.centerx, self.rect.centery + random.randint(-7, 7), self.colour, 30, 6, 0, random.uniform(-2, 2)))

    def update(self, screen):
        self.move_sideways()
        self.draw(screen)
        
class Missile(GameObject):
    def __init__(self, x, y, width, height, colour, speed, max_turn_rate):
        super().__init__(x, y, width, height, colour)
        self.speed = speed
        self.max_turn_rate = max_turn_rate
        self.direction = pygame.math.Vector2(1, 0)

    def update(self, player_pos, screen):
            target_direction = (player_pos - pygame.math.Vector2(self.rect.center)).normalize()
            current_direction = self.direction.normalize()
            new_direction = current_direction.lerp(target_direction, 0.05) 
            self.direction = new_direction.normalize()
            speed_adjustment = current_direction.dot(target_direction)
            adjusted_speed = self.speed * max(speed_adjustment, 0.5)
            self.rect.x += self.direction.x * adjusted_speed
            self.rect.y += self.direction.y * adjusted_speed
            for i in range(1):
                particles.append(Particle(self.rect.centerx + random.randint(-7, 7), self.rect.centery + random.randint(-7, 7), PINK, 30, random.randint(1, 5), random.uniform(-2, 2), random.uniform(-2, 2)))
            self.draw(screen)
            
class Particle:
    def __init__(self, x, y, colour, lifespan=30, initial_size=6, x_velocity=random.uniform(-2, 2), y_velocity=random.uniform(-2, 2)):
        self.x = x
        self.y = y
        self.colour = colour
        self.lifespan = lifespan
        self.size = initial_size
        self.velocity_x = x_velocity
        self.velocity_y = y_velocity

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.lifespan -= 1
        self.size -= self.size / self.lifespan if self.lifespan > 0 else 0 # so it doesn't divide by 0 and then wacky

    def draw(self, screen):
        if self.lifespan > 0 and self.size > 0:
            pygame.draw.circle(screen, self.colour, (int(self.x), int(self.y)), int(self.size))
            
# Colours
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)
BLACK = (0, 0, 0)
PINK = (255, 105, 180)
PURPLE = (128, 0, 128)
RAINBOW = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Player attribute setup
player_size = (25, 25)
player_colour = BLUE
player_x = SCREEN_WIDTH // 2 - player_size[0] // 2
player_y = SCREEN_HEIGHT - player_size[1] - 100
player_velocity = 5
direction = 'R'
cooldown = False
airdash = True
difficulty = 0

# Gravity setup
gravity = 0.5
player_y_velocity = 0
ground_y = SCREEN_HEIGHT - 100

# Setup for the player jumping
is_jumping = False
jump_height = -10

# Obstacle setup
obstacles = []
spawn_rate = 100
obstacle_speed = 5
frame_count = 0
sideways_obstacles = []
sideways_spawn_rate = 150
sideways_spawn_height = ground_y - 150
missile_spawn_timer = 0
missile_spawn_interval = 400
missiles = []
particles = []
refresh = 0

def game_over():
    print("Game Over!")  # uh oh
    print(f"Score: {difficulty}")
    time.sleep(1)
    screen.fill((0, 0, 0))
    game_over_text = font.render(f'Game Over!', True, (WHITE))
    screen.blit(game_over_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 50))
    score_text = font.render(f'Score: {difficulty}', True, (WHITE))
    screen.blit(score_text, (SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//2))
    pygame.display.update()
    time.sleep(3)
    pygame.quit()
    sys.exit()
    running = False
    

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Key presses
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        player_velocity = player_velocity - 1.15
        direction = 'L'
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        player_velocity = player_velocity + 1.15
        direction = 'R'
    if keys[pygame.K_SPACE] and not is_jumping:
        is_jumping = True
        airdash = True
        player_y_velocity = jump_height
    if keys[pygame.K_ESCAPE]:
        running = False
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        if is_jumping:
            player_y_velocity = player_y_velocity + 1
        
    if not keys[pygame.K_LSHIFT] and not cooldown:
        if airdash:
            dash = True
    # Dash 
    if keys[pygame.K_LSHIFT]:
        if dash == True:
            if direction == 'R':
                player_velocity = player_velocity + 30
                for i in range(50):
                    particles.append(Particle(player_x, player_y + random.uniform(-12, 12) + 12, LIGHT_BLUE, 10, random.randint(1, 4), random.randint(2, 16), random.uniform(-5, 5)))
            if direction == 'L':
                player_velocity = player_velocity - 30 
                for i in range(50):
                    particles.append(Particle(player_x, player_y + random.uniform(-12, 12) + 12, LIGHT_BLUE, 10, random.randint(1, 4), random.randint(-16, -2), random.uniform(-5, 5)))
            dash = False
            cooldown = True
            timer = 20
            if is_jumping:
                airdash = False
    if not is_jumping:
        airdash = True             

    difficulty += 1
    if difficulty % 200 == 0:  # Every couple frames, make the game slightly harder and it will spawn more stuff
        spawn_rate = spawn_rate / 1.06
        print(f"Spawn rate: {spawn_rate}")

    # Creating obsticle objects
    # Normal obstacles
    if refresh < 0:
        # Randomly position the new obstacle along the top of the screen
        new_obstacle_x = random.randint(0, SCREEN_WIDTH - 20)
        new_obstacle = Obstacle(new_obstacle_x, 0, 20, 20, (255, 0, 0), obstacle_speed)
        obstacles.append(new_obstacle)
        refresh = spawn_rate
    refresh -= 1
    # Sideways obstacles
    if difficulty > 500:
        if frame_count % sideways_spawn_rate == 0:
            sideways_spawn_height = random.randint(ground_y - 110, ground_y - 20)  # Assuming obstacle height of 20
            new_sideways_obstacle = SidewaysObstacle(SCREEN_WIDTH, sideways_spawn_height, 20, 20, (PURPLE), -5)
            sideways_obstacles.append(new_sideways_obstacle)
    # Tracking missiles
    if missile_spawn_timer >= missile_spawn_interval:
        missiles.append(Missile(SCREEN_WIDTH/2, 0, 20, 20, (PINK), difficulty/300 + 2, difficulty/300 + 2))
        missile_spawn_timer = 0

    frame_count += 1
    missile_spawn_timer += 1
        
    if cooldown:
        if timer == 0:
            cooldown = False
        else:
            timer -= 1

    player_x += player_velocity
    if is_jumping:
        player_velocity = player_velocity/1.19  # Friction
    else:
        player_velocity = player_velocity/1.2  # Friction
        
    # Gravity effect
    if is_jumping:
        player_y += player_y_velocity
        player_y_velocity += gravity
        if player_y >= ground_y - player_size[1]:
            player_y = ground_y - player_size[1]
            is_jumping = False

    # Screen update
    screen.fill((0, 0, 0))
    
    # Draw the player
    if airdash:
        pygame.draw.rect(screen, player_colour, (player_x, player_y, *player_size))
    else:
        pygame.draw.rect(screen, LIGHT_BLUE, (player_x, player_y, *player_size))
          
    for particle in particles[:]:
        particle.update()
        particle.draw(screen)
        if particle.lifespan <= 0:
            particles.remove(particle)

    # Update and draw obstacles
    for obstacle in obstacles[:]:
        obstacle.update(screen)
        if obstacle.rect.colliderect(pygame.Rect(player_x, player_y, *player_size)):
            game_over()
        if obstacle.rect.y > ground_y - 20:
            obstacles.remove(obstacle)
            
    for obstacle in sideways_obstacles[:]:
        obstacle.update(screen)
        if obstacle.rect.colliderect(pygame.Rect(player_x, player_y, *player_size)):
            game_over()
        if obstacle.rect.x < 0 or obstacle.rect.x > SCREEN_WIDTH:
            sideways_obstacles.remove(obstacle)
            
    for missile in missiles[:]:
        missile.update(pygame.math.Vector2(player_x, player_y), screen)
        missile.draw(screen)
        if missile.rect.colliderect(pygame.Rect(player_x, player_y, *player_size)):
            game_over()
        # Remove missile if it touches a wall
        if missile.rect.x < 0 or missile.rect.x > SCREEN_WIDTH or missile.rect.y < 0 or missile.rect.y > ground_y - 20:
            missiles.remove(missile)
            
    pygame.draw.rect(screen, (BLACK), (0, ground_y, SCREEN_WIDTH, 100))  # ground
    pygame.draw.line(screen, (WHITE), (0, ground_y), (SCREEN_WIDTH, ground_y), 2)  # ground line
            
    # Draw the score   
    score_text = font.render(f'Score: {difficulty}', True, (WHITE))
    screen.blit(score_text, (10, 10))  # Should be top left corner
    
    # Draw the insructions
    if difficulty < 400:
        key_inst = font.render(f'WASD / ARROW KEYS: MOVE', True, WHITE)
        screen.blit(key_inst, (10, SCREEN_HEIGHT - 40))
        jump_inst = font.render(f'SPACE: JUMP', True, WHITE)
        screen.blit(jump_inst, (10, SCREEN_HEIGHT - 80))
        dash_inst = font.render(f'SHIFT: DASH', True, WHITE)
        screen.blit(dash_inst, (400, SCREEN_HEIGHT - 40))

    # Update it
    pygame.display.update()

    # Frame rate
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()