import pygame
import math
from Control import Control

# Initialize Pygame
pygame.init()

font = pygame.font.Font("freesansbold.ttf", 24) # Set up font for text

# Brake pedal class
class BrakePedal(Control):
    def __init__(self, pos, scale):
        super().__init__("images/brakePedal.png", pos, scale)
        self.throttling = False
        self.throttle_percent = 0

    def calculate_throttle(self, mouse_pos):
        """Calculate brake throttle based on horizontal mouse position."""
        relative_x = mouse_pos[0] - self.rect.left  # Horizontal position
        throttle = relative_x / self.rect.width  # Normalize between 0-1
        return max(0, min(1, throttle))
    
    def press(self, mouse_pos):
        """Activate brake when pressed."""
        self.throttling = True
        self.update_throttle(mouse_pos)
        
    def release(self):
        """Reset throttle when released."""
        self.throttling = False
        self.throttle_percent = 0
    
    def update_throttle(self, mouse_pos):
        """Update throttle level."""
        self.throttle_percent = int(self.calculate_throttle(mouse_pos) * 100)
    
    def draw(self, surface):
        """Draw pedal and display throttle percentage."""
        super().draw(surface)

        if self.throttling:
            indicator_width = int((self.throttle_percent / 100) * self.rect.width)
            gradient_surface = pygame.Surface((indicator_width, self.rect.height), pygame.SRCALPHA)

            # Extract alpha channel from gas pedal image
            alpha_mask = pygame.surfarray.pixels_alpha(self.original_image)

            for x in range(indicator_width):  # Loop horizontally for left-to-right gradient
                ratio = x / indicator_width  # Gradient progression
                color = (int(255 * ratio), int(255 * (1 - ratio)), 0, 120)  # Smooth gradient

                for y in range(self.rect.height):
                    if 0 <= x < self.rect.width and 0 <= y < self.rect.height:
                        if alpha_mask[x, y]:  # Apply only on non-transparent pixels
                            gradient_surface.set_at((x, y), color)

            del alpha_mask  # Avoid memory issues

            surface.blit(gradient_surface, (self.rect.left, self.rect.top))  # Correct position

            throttle_text = font.render(f"Throttle: {self.throttle_percent}%", True, (0, 0, 0))
            surface.blit(throttle_text, (self.rect.left, self.rect.bottom + 10))
