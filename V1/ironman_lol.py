import pygame
import sys
import math
from datetime import datetime
import random

# Init
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
width, height = screen.get_size()
pygame.display.set_caption("JARVIS HUD")

# Fonts
try:
    font_large = pygame.font.Font("Orbitron-Bold.ttf", 36)
    font_small = pygame.font.Font("Orbitron-Regular.ttf", 24)
except:
    font_large = pygame.font.SysFont("Arial", 36)
    font_small = pygame.font.SysFont("Arial", 24)

# Colors
CYAN = (0, 255, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

clock = pygame.time.Clock()

# Battery UI
def draw_battery(x, y, level=0.75):
    pygame.draw.rect(screen, CYAN, (x, y, 60, 25), 2)
    pygame.draw.rect(screen, CYAN, (x + 4, y + 4, int(52 * level), 17))
    pygame.draw.rect(screen, CYAN, (x + 60, y + 7, 6, 11))

# Central HUD
def draw_rotating_rings(center, frame):
    layers = [
        {"radius": 80, "lines": 12, "speed": 1},
        {"radius": 110, "lines": 24, "speed": -0.5},
        {"radius": 140, "lines": 36, "speed": 0.25},
    ]
    for layer in layers:
        r = layer["radius"]
        lines = layer["lines"]
        rotation = frame * layer["speed"]
        for i in range(lines):
            angle_deg = i * (360 / lines) + rotation
            angle_rad = math.radians(angle_deg)
            x1 = center[0] + r * math.cos(angle_rad)
            y1 = center[1] + r * math.sin(angle_rad)
            x2 = center[0] + (r + 10) * math.cos(angle_rad)
            y2 = center[1] + (r + 10) * math.sin(angle_rad)
            pygame.draw.line(screen, CYAN, (x1, y1), (x2, y2), 1)
        pygame.draw.circle(screen, CYAN, center, r, 1)

# Target reticle
def draw_target(center, frame):
    pygame.draw.circle(screen, CYAN, center, 10, 1)
    pygame.draw.line(screen, CYAN, (center[0] - 15, center[1]), (center[0] - 5, center[1]), 1)
    pygame.draw.line(screen, CYAN, (center[0] + 5, center[1]), (center[0] + 15, center[1]), 1)
    pygame.draw.line(screen, CYAN, (center[0], center[1] - 15), (center[0], center[1] - 5), 1)
    pygame.draw.line(screen, CYAN, (center[0], center[1] + 5), (center[0], center[1] + 15), 1)

# Voice waveform
def draw_waveform(frame, center_x, bottom_y):
    width = 300
    bar_count = 50
    bar_width = width // bar_count
    for i in range(bar_count):
        height_mod = math.sin((frame * 0.2 + i) * 0.3) * 10 + random.randint(1, 5)
        bar_height = 10 + height_mod
        x = center_x - width // 2 + i * bar_width
        pygame.draw.rect(screen, CYAN, (x, bottom_y - bar_height, bar_width - 1, bar_height))

# Side sensor bars
def draw_sensor_bars(x, top, bottom, frame):
    num_bars = 20
    bar_height = (bottom - top) // num_bars
    for i in range(num_bars):
        intensity = math.sin(frame * 0.1 + i) * 0.5 + 0.5
        color = (0, int(100 + 155 * intensity), int(255 * intensity))
        pygame.draw.rect(screen, color, (x, top + i * bar_height, 10, bar_height - 2))

# Main loop
frame = 0
center = (width // 2, height // 2)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            pygame.quit()
            sys.exit()

    screen.fill(BLACK)

    # Header
    now = datetime.now().strftime("%H:%M:%S")
    screen.blit(font_large.render(now, True, CYAN), (30, 30))
    draw_battery(width - 100, 30)

    # Notifications
    pygame.draw.rect(screen, (0, 255, 255, 40), (0, height - 60, width, 50))
    notif = font_small.render("HUD SYSTEM ACTIVE ? SCANNING", True, CYAN)
    screen.blit(notif, (30, height - 50))

    # HUD
    draw_rotating_rings(center, frame)
    draw_target(center, frame)
    draw_waveform(frame, center[0], height - 70)
    draw_sensor_bars(20, 100, height - 100, frame)
    draw_sensor_bars(width - 30, 100, height - 100, frame)

    pygame.display.flip()
    clock.tick(60)
    frame += 1
