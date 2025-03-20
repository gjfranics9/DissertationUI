import pygame
import math
from Control import Control

# Initialize Pygame
pygame.init()

font = pygame.font.Font("freesansbold.ttf", 24) # Set up font for text

# Gas pedal class
class GasPedal(Control):
    def __init__(self, pos, scale):
        '''Initialize gas pedal object.'''
        super().__init__("images/gasPedal.png", pos, scale)
        self.throttling = False
        self.throttle_percent = 0

    def calculate_throttle(self, mouse_pos):
        """Calculate throttle based on mouse position."""
        relative_y = mouse_pos[1] - self.rect.top
        throttle = 1 - (relative_y / self.rect.height)
        return max(0, min(1, throttle))

    def press(self, mouse_pos):
        """Activate throttle when pressed."""
        self.throttling = True
        self.update_throttle(mouse_pos)

    def release(self):
        """Reset throttle when released."""
        self.throttling = False
        self.throttle_percent = 0

    def update_throttle(self, mouse_pos):
        """Update throttle level."""
        self.throttle_percent = int(self.calculate_throttle(mouse_pos) * 100)

    def getThrottle(self):
        """Return throttle percentage."""
        return self.throttle_percent/100

    def draw(self, surface):
        """Draw pedal and display throttle percentage."""
        super().draw(surface)
        if self.throttling:
            indicator_height = (self.throttle_percent / 100) * self.rect.height
            gradient_surface = pygame.Surface((self.rect.width, int(indicator_height)), pygame.SRCALPHA)

            # Extract alpha channel from gas pedal image
            alpha_mask = pygame.surfarray.pixels_alpha(self.original_image)

            for y in range(int(indicator_height)): # Loop vertically for top-to-bottom gradient
                ratio = y / indicator_height
                color = (int(255 * ratio), int(255 * (1 - ratio)), 0, 120)

                # Apply alpha mask to ensure transparency is maintained
                for x in range(self.rect.width):
                    # Only modify non-transparent pixels
                    if alpha_mask[x, int(self.rect.height - indicator_height + y)]:  # Only modify non-transparent pixels
                        gradient_surface.set_at((x, y), color)

            del alpha_mask  # Avoid memory issues with surfarray

            surface.blit(gradient_surface, (self.rect.left, self.rect.bottom - indicator_height))

            throttle_text = font.render(f"Throttle: {self.throttle_percent}%", True, (0, 0, 0))
            surface.blit(throttle_text, (self.rect.left, self.rect.bottom + 10))
