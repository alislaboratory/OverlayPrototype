import pygame
import sys
import math
from datetime import datetime

# Initialize Pygame
pygame.init()

# Set up display
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
width, height = screen.get_size()
pygame.display.set_caption("Smart Glasses UI")

# Set up fonts
font_large = pygame.font.SysFont('Arial', 36)
font_small = pygame.font.SysFont('Arial', 24)

# Colors
WHITE = (255, 255, 255)
TRANSPARENT_WHITE = (255, 255, 255, 128)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Clock for frame updates
clock = pygame.time.Clock()

# Helper to draw battery indicator
def draw_battery(surface, x, y, width=60, height=25, level=0.75):
    pygame.draw.rect(surface, WHITE, (x, y, width, height), 2)
    pygame.draw.rect(surface, GREEN, (x + 4, y + 4, int((width - 8) * level), height - 8))
    pygame.draw.rect(surface, WHITE, (x + width, y + height // 3, 6, height // 3))

# Spinner variables
angle = 0
spinner_radius = 30
spinner_length = 20
spinner_center = (width // 2, height // 2)

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            pygame.quit()
            sys.exit()

    screen.fill(BLACK)

    # Draw time (top-left)
    current_time = datetime.now().strftime("%H:%M")
    time_text = font_large.render(current_time, True, WHITE)
    screen.blit(time_text, (30, 30))

    # Draw battery (top-right)
    draw_battery(screen, width - 100, 30)

    # Draw notifications bar (bottom)
    notification_surface = pygame.Surface((width, 50), pygame.SRCALPHA)
    notification_surface.fill((255, 255, 255, 40))
    screen.blit(notification_surface, (0, height - 60))
    notif_text = font_small.render("No new notifications", True, WHITE)
    screen.blit(notif_text, (30, height - 50))

    # Draw animated spinner (center)
    end_x = spinner_center[0] + spinner_radius * math.cos(math.radians(angle))
    end_y = spinner_center[1] + spinner_radius * math.sin(math.radians(angle))
    pygame.draw.line(screen, WHITE, spinner_center, (end_x, end_y), 4)

    angle = (angle + 5) % 360  # Rotate spinner

    pygame.display.flip()
    clock.tick(30)
