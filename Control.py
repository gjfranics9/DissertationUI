import pygame

# Initialize Pygame
pygame.init()

# Base class for interactive controls (steering wheel, pedals, etc.)
class Control:
    def __init__(self, img_path, pos, scale):
        """Initialize a generic control object."""
        original_image = pygame.image.load(img_path).convert_alpha()
        self.original_image = pygame.transform.scale(original_image, scale)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=pos)
        

    def draw(self, surface):
        """Draw control on the screen."""
        surface.blit(self.image, self.rect)

    def press(self):
        """To be defined by subclasses."""
        pass