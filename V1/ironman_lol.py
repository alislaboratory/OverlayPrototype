import pygame
import sys
import math
from datetime import datetime

# Initialize Pygame
pygame.init()

# Display setup
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
width, height = screen.get_size()
pygame.display.set_caption("HUD UI")

# Fonts
font_large = pygame.font.SysFont('Arial', 36)
font_small = pygame.font.SysFont('Arial', 24)

# Colors
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
TRANSPARENT_CYAN = (0, 255, 255, 100)
BLACK = (0, 0, 0)

# Clock
clock = pygame.time.Clock()

# Battery indicator
def draw_battery(surface, x, y, width=60, height=25, level=0.75):
    pygame.draw.rect(surface, WHITE, (x, y, width, height), 2)
    pygame.draw.rect(surface, CYAN, (x + 4, y + 4, int((width - 8) * level), height - 8))
    pygame.draw.rect(surface, WHITE, (x + width, y + height // 3, 6, height // 3))

# Draw rotating HUD
def draw_hud(center, frame_count):
    # Base HUD layers
    layers = [
        {"radius": 80, "lines": 12, "speed": 1},
        {"radius": 110, "lines": 24, "speed": -0.5},
        {"radius": 140, "lines": 36, "speed": 0.25},
    ]

    for layer in layers:
        r = layer["radius"]
        lines = layer["lines"]
        rotation = frame_count * layer["speed"]
        for i in range(lines):
            angle_deg = i * (360 / lines) + rotation
            angle_rad = math.radians(angle_deg)
            x1 = center[0] + r * math.cos(angle_rad)
            y1 = center[1] + r * math.sin(angle_rad)
            x2 = center[0] + (r + 10) * math.cos(angle_rad)
            y2 = center[1] + (r + 10) * math.sin(angle_rad)
            pygame.draw.line(screen, CYAN, (x1, y1), (x2, y2), 1)
        pygame.draw.circle(screen, CYAN, center, r, 1)

    # Pulsing core
    pulse_radius = 20 + int(math.sin(pygame.time.get_ticks() * 0.005) * 5)
    pygame.draw.circle(screen, CYAN, center, pulse_radius, 2)
    pygame.draw.line(screen, CYAN, (center[0] - 10, center[1]), (center[0] + 10, center[1]), 1)
    pygame.draw.line(screen, CYAN, (center[0], center[1] - 10), (center[0], center[1] + 10), 1)

# Main loop
frame = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            pygame.quit()
            sys.exit()

    screen.fill(BLACK)

    # UI: Time
    current_time = datetime.now().strftime("%H:%M")
    time_text = font_large.render(current_time, True, CYAN)
    screen.blit(time_text, (30, 30))

    # UI: Battery
    draw_battery(screen, width - 100, 30)

    # UI: Notifications
    notification_surface = pygame.Surface((width, 50), pygame.SRCALPHA)
    notification_surface.fill((0, 255, 255, 40))
    screen.blit(notification_surface, (0, height - 60))
    notif_text = font_small.render("System online. All sensors nominal.", True, CYAN)
    screen.blit(notif_text, (30, height - 50))

    # Central Iron-Man-style HUD
    draw_hud((width // 2, height // 2), frame)

    pygame.display.flip()
    frame += 1
    clock.tick(60)
