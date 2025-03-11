import pygame
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_DIM = (1280, 720)  # Screen resolution
BACKGROUND_COLOR = (0x93, 0x95, 0x97)  # Background color
FPS = 60  # Frames per second

# Set up display, clock, and font
screen = pygame.display.set_mode(SCREEN_DIM, pygame.SRCALPHA)
clock = pygame.time.Clock()
font = pygame.font.Font("freesansbold.ttf", 24)

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

# Steering wheel class with rotation and recentering
class Wheel(Control):
    def __init__(self, pos, scale):
        super().__init__("images/steeringWheel.png", pos, scale)
        self.angle = 0
        self.dragging = False
        self.initial_mouse_angle = 0
        self.initial_wheel_angle = 0
        self.max_rotation_speed = 5  # Limit rotation speed

    def rotate(self, angle):
        """Rotate the wheel with constraints."""
        target_angle = max(-90, min(90, angle))  # Constrain within -90 to 90 degrees
        angle_difference = target_angle - self.angle
        if abs(angle_difference) > self.max_rotation_speed:
            angle_difference = math.copysign(self.max_rotation_speed, angle_difference)
        self.angle += angle_difference
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def calculate_angle(self, mouse_pos):
        """Calculate angle between mouse and wheel center."""
        dx, dy = mouse_pos[0] - self.rect.centerx, mouse_pos[1] - self.rect.centery
        return math.degrees(math.atan2(-dy, dx))

    def angle_difference(self, current, initial):
        """Calculate shortest rotational difference."""
        return (current - initial + 180) % 360 - 180

    def start_drag(self, mouse_pos):
        """Begin dragging the wheel."""
        self.dragging = True
        self.initial_mouse_angle = self.calculate_angle(mouse_pos)
        self.initial_wheel_angle = self.angle

    def update_rotation(self, mouse_pos):
        """Update wheel rotation based on mouse movement."""
        current_mouse_angle = self.calculate_angle(mouse_pos)
        angle_diff = self.angle_difference(current_mouse_angle, self.initial_mouse_angle)
        self.rotate(self.initial_wheel_angle + angle_diff)

    def return_to_center(self):
        """Gradually return wheel to center when not in use."""
        if abs(self.angle) > 1:
            self.rotate(self.angle - 2 * math.copysign(1, self.angle))
        else:
            self.rotate(0)
            
# Gas pedal class
class GasPedal(Control):
    def __init__(self, pos, scale):
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

    def draw(self, surface):
        """Draw pedal and display throttle percentage."""
        super().draw(surface)
        if self.throttling:
            indicator_height = (self.throttle_percent / 100) * self.rect.height
            gradient_surface = pygame.Surface((self.rect.width, int(indicator_height)), pygame.SRCALPHA)

            # Extract alpha channel from gas pedal image
            alpha_mask = pygame.surfarray.pixels_alpha(self.original_image)

            for y in range(int(indicator_height)):
                ratio = y / indicator_height
                color = (int(255 * ratio), int(255 * (1 - ratio)), 0, 120)

                # Apply alpha mask to ensure transparency is maintained
                for x in range(self.rect.width):
                    if alpha_mask[x, int(self.rect.height - indicator_height + y)]:  # Only modify non-transparent pixels
                        gradient_surface.set_at((x, y), color)

            del alpha_mask  # Avoid memory issues with surfarray

            surface.blit(gradient_surface, (self.rect.left, self.rect.bottom - indicator_height))

            throttle_text = font.render(f"Throttle: {self.throttle_percent}%", True, (0, 0, 0))
            surface.blit(throttle_text, (self.rect.left, self.rect.bottom + 10))

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



# Instantiate controls
wheel = Wheel((0.2675 * SCREEN_DIM[0], 0.4733 * SCREEN_DIM[1]),
              (int(0.375 * SCREEN_DIM[0]), int((2 / 3) * SCREEN_DIM[1])))

gas_pedal = GasPedal((0.6325 * SCREEN_DIM[0], 0.51 * SCREEN_DIM[1]),
                     (int(0.14 * SCREEN_DIM[0]), int(0.52 * SCREEN_DIM[1])))

brake_pedal = BrakePedal((0.845 * SCREEN_DIM[0], 0.625 * SCREEN_DIM[1]),
                         (int(0.25 * SCREEN_DIM[0]), int(0.25 * SCREEN_DIM[1])))

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            if wheel.rect.collidepoint(mouse_pos):
                wheel.start_drag(mouse_pos)
            elif gas_pedal.rect.collidepoint(mouse_pos):
                gas_pedal.press(mouse_pos)
            elif brake_pedal.rect.collidepoint(mouse_pos):
                brake_pedal.press(mouse_pos)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            wheel.dragging = False
            gas_pedal.release()
            brake_pedal.release()

        elif event.type == pygame.MOUSEMOTION: # Update control states based on mouse movement
            mouse_pos = event.pos
            if wheel.dragging:
                wheel.update_rotation(mouse_pos)   # Update wheel rotation based on mouse movement
            if gas_pedal.throttling:
                gas_pedal.update_throttle(mouse_pos)  # Update throttle based on mouse position
            if brake_pedal.throttling:
                brake_pedal.update_throttle(mouse_pos)  # Update throttle based on mouse position   

    # Springs the wheel back to the middle
    if not wheel.dragging:
        wheel.return_to_center()

    # Render elements
    background = pygame.image.load("images/background.png")
    background = pygame.transform.scale(background, (screen.get_width(), screen.get_height()))
    screen.blit(background, (0, 0))
    
    wheel.draw(screen)
    gas_pedal.draw(screen)
    brake_pedal.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()