import pygame
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_DIM = (1280, 720)  # Screen resolution
BACKGROUND_COLOR = (0x93, 0x95, 0x97)  # Gray background color
FPS = 60  # Frame rate

# Set up display, clock, and font
screen = pygame.display.set_mode(SCREEN_DIM, pygame.SRCALPHA)
clock = pygame.time.Clock()
font = pygame.font.Font("freesansbold.ttf", 24)

# Base class for interactive controls (steering wheel, pedals, etc.)
class Control:
    def __init__(self, img_path, pos, scale):
        """Initialize a generic control element."""
        original_image = pygame.image.load(img_path).convert_alpha()
        self.original_image = pygame.transform.scale(original_image, scale)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=pos)

    def draw(self, surface):
        """Draw the control on the screen."""
        surface.blit(self.image, self.rect)

    def press(self):
        """Define behavior when pressed (to be implemented by subclasses)."""
        pass

# Steering wheel class with rotation and smooth recentering
class Wheel(Control):
    def __init__(self, pos, scale):
        """Initialize the steering wheel."""
        super().__init__("images/steeringWheel.png", pos, scale)
        self.angle = 0  # Current rotation angle
        self.dragging = False  # Is the wheel being dragged?
        self.initial_mouse_angle = 0  # Mouse angle at the start of drag
        self.initial_wheel_angle = 0  # Initial wheel angle at start of drag
        self.max_rotation_speed = 5  # Limits max rotation per frame

    def rotate(self, angle):
        """Rotate the wheel with constraints."""
        target_angle = max(-90, min(90, angle))  # Clamp rotation
        angle_difference = target_angle - self.angle
        if abs(angle_difference) > self.max_rotation_speed:
            angle_difference = math.copysign(self.max_rotation_speed, angle_difference)
        self.angle += angle_difference
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def calculate_angle(self, mouse_pos):
        """Calculate the angle between the wheel center and the mouse."""
        dx, dy = mouse_pos[0] - self.rect.centerx, mouse_pos[1] - self.rect.centery
        return math.degrees(math.atan2(-dy, dx))

    def angle_difference(self, current, initial):
        """Compute minimal angle difference to avoid snapping."""
        return (current - initial + 180) % 360 - 180

    def start_drag(self, mouse_pos):
        """Start tracking mouse movement for rotation."""
        self.dragging = True
        self.initial_mouse_angle = self.calculate_angle(mouse_pos)
        self.initial_wheel_angle = self.angle

    def update_rotation(self, mouse_pos):
        """Update wheel rotation based on mouse movement."""
        current_mouse_angle = self.calculate_angle(mouse_pos)
        angle_diff = self.angle_difference(current_mouse_angle, self.initial_mouse_angle)
        desired_angle = self.initial_wheel_angle + angle_diff
        self.rotate(desired_angle)

    def return_to_center(self):
        """Gradually return the wheel to the center when not being dragged."""
        if abs(self.angle) > 1:
            self.rotate(self.angle - 2 * math.copysign(1, self.angle))
        else:
            self.rotate(0)

# Gas pedal class with throttle visualization
class GasPedal(Control):
    def __init__(self, pos, scale):
        """Initialize the gas pedal."""
        super().__init__("images/gasPedal.png", pos, scale)
        self.throttling = False
        self.throttle_percent = 0

    def calculate_throttle(self, mouse_pos):
        """Calculate throttle percentage based on mouse position."""
        relative_y = mouse_pos[1] - self.rect.top
        throttle = 1 - (relative_y / self.rect.height)
        return max(0, min(1, throttle))

    def press(self, mouse_pos):
        """Activate throttle on press."""
        self.throttling = True
        self.update_throttle(mouse_pos)

    def release(self):
        """Deactivate throttle."""
        self.throttling = False
        self.throttle_percent = 0

    def update_throttle(self, mouse_pos):
        """Update throttle percentage."""
        self.throttle_percent = int(self.calculate_throttle(mouse_pos) * 100)

    def draw(self, surface):
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
    
    def press(self):
        print("Brake activated")

# Instantiate controls
wheel = Wheel((343, 341), (480, 480))
gas_pedal = GasPedal((810, 367), (180, 374))
brake_pedal = BrakePedal((1083, 450), (320, 180))

# Main event loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if wheel.rect.collidepoint(event.pos):
                wheel.start_drag(event.pos)
            elif gas_pedal.rect.collidepoint(event.pos):
                gas_pedal.press(event.pos)
            elif brake_pedal.rect.collidepoint(event.pos):
                brake_pedal.press()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            wheel.dragging = False
            gas_pedal.release()
        elif event.type == pygame.MOUSEMOTION:
            if wheel.dragging:
                wheel.update_rotation(event.pos)
            if gas_pedal.throttling:
                gas_pedal.update_throttle(event.pos)
    if not wheel.dragging:
        wheel.return_to_center()
    
    screen.fill(BACKGROUND_COLOR)
    wheel.draw(screen)
    gas_pedal.draw(screen)
    brake_pedal.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
