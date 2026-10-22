import pygame
import sys
import requests
import random

# 1. INITIALIZE ENGINE & SETUP WINDOW
pygame.init()
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FighTT")
clock = pygame.time.Clock()
FPS = 60

SERVER_URL = "http://127.0.0.1:8000"

# Strict Universal Color Palette
BACKGROUND = (25, 20, 30)
GROUND_COLOR = (55, 50, 65)
WEAPON_COLOR = (240, 200, 40)
TEXT_COLOR = (245, 245, 245)
SKIN_COLOR = (240, 190, 150)
PANTS_COLOR = (45, 45, 55)
BOOTS_COLOR = (85, 55, 35)
STEEL_COLOR = (180, 190, 200)

P1_NAME = "Human_Player"
CPU_NAME = "Computer_AI"

# Safe Registration Setup
try:
    # Set a tiny timeout (0.5 seconds) so it doesn't freeze the window on boot
    requests.post(f"{SERVER_URL}/register", json={"username": P1_NAME}, timeout=0.5)
    requests.post(f"{SERVER_URL}/register", json={"username": CPU_NAME}, timeout=0.5)
    print("Connected to server successfully!")
except (requests.exceptions.RequestException, requests.exceptions.Timeout):
    print("Warning: Running in offline mode.")

# 2. ADVANCED HUMAN FIGHTER CLASS
class HumanFighter:
    def __init__(self, x, y, shirt_color, hair_color, name, is_cpu=False):
        self.rect = pygame.Rect(x, y, 40, 64)
        self.shirt_color = shirt_color
        self.hair_color = hair_color
        self.name = name
        self.is_cpu = is_cpu
        
        self.current_state = "IDLE"  
        self.walk_frame = 0
        self.direction = 1 
        
        self.vx = 0
        self.vy = 0
        self.is_jumping = False
        
        self.hp = 100
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 25
        self.weapon_range = 55
        self.weapon_damage = 12
        self.weapon_rect = pygame.Rect(0, 0, 0, 0)

    def handle_human_input(self, keys):
        self.vx = 0
        if keys[pygame.K_a]:
            self.vx = -5
            self.direction = -1
            self.current_state = "WALK"
        elif keys[pygame.K_d]:
            self.vx = 5
            self.direction = 1
            self.current_state = "WALK"
        else:
            self.current_state = "IDLE"

        if keys[pygame.K_w] and not self.is_jumping:
            self.vy = -14
            self.is_jumping = True

        if keys[pygame.K_f] and not self.attack_timer:
            self.attack_timer = self.attack_cooldown

    def handle_cpu_behavior(self, target):
        self.vx = 0
        distance_x = target.rect.centerx - self.rect.centerx
        abs_distance_x = abs(distance_x)
        
        if distance_x > 0: self.direction = 1
        elif distance_x < 0: self.direction = -1

        if abs_distance_x > (self.weapon_range + 10):
            self.vx = 4 * self.direction
            self.current_state = "WALK"
        else:
            self.current_state = "IDLE"
            if not self.attack_timer and random.random() < 0.15:
                self.attack_timer = self.attack_cooldown

    def update(self):
        self.vy += 0.8
        self.rect.x += self.vx
        self.rect.y += self.vy

        if self.rect.bottom >= HEIGHT - 60:
            self.rect.bottom = HEIGHT - 60
            self.vy = 0
            self.is_jumping = False
            
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > WIDTH: self.rect.right = WIDTH

        if self.current_state == "WALK":
            self.walk_frame += 0.2
            if self.walk_frame >= 2: self.walk_frame = 0
        else:
            self.walk_frame = 0

        if self.attack_timer > 0:
            self.current_state = "ATTACK"
            if self.attack_timer > self.attack_cooldown - 6:
                self.is_attacking = True
                if self.direction == 1:
                    self.weapon_rect = pygame.Rect(self.rect.right, self.rect.centery - 10, self.weapon_range, 20)
                else:
                    self.weapon_rect = pygame.Rect(self.rect.left - self.weapon_range, self.rect.centery - 10, self.weapon_range, 20)
            else:
                self.is_attacking = False
                self.weapon_rect = pygame.Rect(0, 0, 0, 0)
            self.attack_timer -= 1
        else:
            self.is_attacking = False
            self.weapon_rect = pygame.Rect(0, 0, 0, 0)

    def draw(self, surface):
        x, y = self.rect.x, self.rect.y
        
        pygame.draw.rect(surface, self.hair_color, (x + 12, y, 16, 12))
        pygame.draw.rect(surface, SKIN_COLOR, (x + 14, y + 12, 12, 10))
        pygame.draw.rect(surface, self.shirt_color, (x + 10, y + 22, 20, 20))
        
        frame = int(self.walk_frame)
        if self.current_state == "WALK" and frame == 1:
            pygame.draw.rect(surface, PANTS_COLOR, (x + 10, y + 42, 8, 14))
            pygame.draw.rect(surface, PANTS_COLOR, (x + 22, y + 42, 8, 8))
            pygame.draw.rect(surface, BOOTS_COLOR, (x + 8, y + 56, 10, 8))
            pygame.draw.rect(surface, BOOTS_COLOR, (x + 22, y + 50, 10, 8))
        elif self.current_state == "WALK" and frame == 0:
            pygame.draw.rect(surface, PANTS_COLOR, (x + 10, y + 42, 8, 8))
            pygame.draw.rect(surface, PANTS_COLOR, (x + 22, y + 42, 8, 14))
            pygame.draw.rect(surface, BOOTS_COLOR, (x + 10, y + 50, 10, 8))
            pygame.draw.rect(surface, BOOTS_COLOR, (x + 22, y + 56, 10, 8))
        else: 
            pygame.draw.rect(surface, PANTS_COLOR, (x + 11, y + 42, 7, 14))
            pygame.draw.rect(surface, PANTS_COLOR, (x + 22, y + 42, 7, 14))
            pygame.draw.rect(surface, BOOTS_COLOR, (x + 9, y + 56, 9, 8))
            pygame.draw.rect(surface, BOOTS_COLOR, (x + 22, y + 56, 9, 8))

        if self.current_state == "ATTACK":
            if self.direction == 1:
                pygame.draw.rect(surface, SKIN_COLOR, (x + 30, y + 24, 12, 6)) 
                pygame.draw.rect(surface, STEEL_COLOR, (x + 42, y + 10, 6, 24)) 
            else:
                pygame.draw.rect(surface, SKIN_COLOR, (x - 2, y + 24, 12, 6))
                pygame.draw.rect(surface, STEEL_COLOR, (x - 8, y + 10, 6, 24))
        else:
            if self.direction == 1:
                pygame.draw.rect(surface, SKIN_COLOR, (x + 4, y + 24, 6, 12))
                pygame.draw.rect(surface, STEEL_COLOR, (x + 2, y + 20, 4, 16))
            else:
                pygame.draw.rect(surface, SKIN_COLOR, (x + 30, y + 24, 6, 12))
                pygame.draw.rect(surface, STEEL_COLOR, (x + 34, y + 20, 4, 16))

# 4. GAME INITIALIZATION
player1 = HumanFighter(150, 200, (50, 120, 240), (90, 60, 40), P1_NAME)
cpu_opponent = HumanFighter(600, 200, (220, 60, 60), (200, 180, 50), CPU_NAME, is_cpu=True)

font = pygame.font.SysFont("arial", 22, bold=True)
game_over = False
winner_text = ""

def send_match_report(winner, loser):
    try:
        payload = {"winner_username": winner, "loser_username": loser}
        # Fixed timeout down to 0.5s so it never freezes the window loop if server fails
        requests.post(f"{SERVER_URL}/match/report", json=payload, timeout=0.5)
    except (requests.exceptions.RequestException, requests.exceptions.Timeout):
        pass

# Main Loop Engine
while True:
    screen.fill(BACKGROUND)
    pygame.draw.rect(screen, GROUND_COLOR, pygame.Rect(0, HEIGHT - 60, WIDTH, 60))

    # CRUCIAL: Process Pygame Events to prevent Windows from freezing the screen
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    if not game_over:
        player1.handle_human_input(keys)
        cpu_opponent.handle_cpu_behavior(target=player1)
        
        player1.update()
        cpu_opponent.update()

        if player1.is_attacking and player1.weapon_rect.colliderect(cpu_opponent.rect):
            cpu_opponent.hp -= player1.weapon_damage
            player1.weapon_rect = pygame.Rect(0,0,0,0) 
            
        if cpu_opponent.is_attacking and cpu_opponent.weapon_rect.colliderect(player1.rect):
            player1.hp -= cpu_opponent.weapon_damage
            cpu_opponent.weapon_rect = pygame.Rect(0,0,0,0)

        if player1.hp <= 0 or cpu_opponent.hp <= 0:
            game_over = True
            if player1.hp <= 0 and cpu_opponent.hp <= 0:
                winner_text = "TIE MATCH!"
            elif player1.hp <= 0:
                winner_text = f"{cpu_opponent.name} WINS!"
                send_match_report(cpu_opponent.name, player1.name)
            else:
                winner_text = f"{player1.name} WINS!"
                send_match_report(player1.name, cpu_opponent.name)

    player1.draw(screen)
    cpu_opponent.draw(screen)

    pygame.draw.rect(screen, (80, 20, 20), (30, 20, 220, 18))
    pygame.draw.rect(screen, (40, 220, 80), (30, 20, max(0, player1.hp * 2.2), 18))
    screen.blit(font.render(f"{player1.name}", True, TEXT_COLOR), (30, 42))

    pygame.draw.rect(screen, (80, 20, 20), (WIDTH - 250, 20, 220, 18))
    pygame.draw.rect(screen, (40, 220, 80), (WIDTH - 250, 20, max(0, cpu_opponent.hp * 2.2), 18))
    screen.blit(font.render(f"{cpu_opponent.name}", True, TEXT_COLOR), (WIDTH - 250, 42))

    if game_over:
        end_lbl = font.render(winner_text, True, WEAPON_COLOR)
        sub_lbl = font.render("Press ESCAPE to Close Game", True, TEXT_COLOR)
        screen.blit(end_lbl, (WIDTH // 2 - end_lbl.get_width() // 2, HEIGHT // 2 - 30))
        screen.blit(sub_lbl, (WIDTH // 2 - sub_lbl.get_width() // 2, HEIGHT // 2 + 10))
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()

    pygame.display.flip()
    clock.tick(FPS)
