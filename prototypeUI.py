import pygame
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_DIM = (1280, 720)
BACKGROUND_COLOR = (0x93, 0x95, 0x97)
FPS = 60

# Set up display, clock, and font
screen = pygame.display.set_mode(SCREEN_DIM, pygame.SRCALPHA)
clock = pygame.time.Clock()
font = pygame.font.Font("freesansbold.ttf", 24)

# Base class for interactive controls (steering wheel, pedals, etc.)
class Control:
    def __init__(self, img_path, pos, scale):
        original_image = pygame.image.load(img_path).convert_alpha()
        self.original_image = pygame.transform.scale(original_image, scale)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=pos)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def press(self):
        pass  # Defined by subclasses

# Steering wheel class with rotation and smooth recentering
class Wheel(Control):
    def __init__(self, pos, scale):
        super().__init__("images/steeringWheel.png", pos, scale)
        self.angle = 0
        self.dragging = False
        self.initial_mouse_angle = 0
        self.initial_wheel_angle = 0
        self.max_rotation_speed = 5

    def rotate(self, angle):
        target_angle = max(-90, min(90, angle))
        angle_difference = target_angle - self.angle
        if abs(angle_difference) > self.max_rotation_speed:
            angle_difference = math.copysign(self.max_rotation_speed, angle_difference)
        self.angle += angle_difference
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def calculate_angle(self, mouse_pos):
        dx, dy = mouse_pos[0] - self.rect.centerx, mouse_pos[1] - self.rect.centery
        return math.degrees(math.atan2(-dy, dx))

    def angle_difference(self, current, initial):
        # Ensures minimal rotation angle difference to avoid snapping
        diff = (current - initial + 180) % 360 - 180
        return diff

    def start_drag(self, mouse_pos):
        self.dragging = True
        self.initial_mouse_angle = self.calculate_angle(mouse_pos)
        self.initial_wheel_angle = self.angle

    def update_rotation(self, mouse_pos):
        current_mouse_angle = self.calculate_angle(mouse_pos)
        angle_diff = self.angle_difference(current_mouse_angle, self.initial_mouse_angle)
        desired_angle = self.initial_wheel_angle + angle_diff
        self.rotate(desired_angle)

    def return_to_center(self):
        if abs(self.angle) > 1:
            self.rotate(self.angle - 2 * math.copysign(1, self.angle))
        else:
            self.rotate(0)

class GasPedal(Control):
    def __init__(self, pos, scale):
        super().__init__("images/gasPedal.png", pos, scale)
        self.throttling = False
        self.throttle_percent = 0

    def calculate_throttle(self, mouse_pos):
        relative_y = mouse_pos[1] - self.rect.top
        throttle = 1 - (relative_y / self.rect.height)
        return max(0, min(1, throttle))

    def press(self, mouse_pos):
        self.throttling = True
        self.update_throttle(mouse_pos)

    def release(self):
        self.throttling = False
        self.throttle_percent = 0

    def update_throttle(self, mouse_pos):
        self.throttle_percent = int(self.calculate_throttle(mouse_pos) * 100)

    def draw(self, surface):
        super().draw(surface)

        # Draw throttle indicator (translucent gradient)
        if self.throttling:
            indicator_height = (self.throttle_percent / 100) * self.rect.height
            gradient_surface = pygame.Surface((self.rect.width, int(indicator_height)), pygame.SRCALPHA)

            for y in range(int(indicator_height)):
                ratio = y / indicator_height
                color = (
                    int(255 * ratio),
                    int(255 * (1 - ratio)),
                    0,
                    120
                )
                pygame.draw.line(gradient_surface, color, (0, indicator_height - y), (self.rect.width, indicator_height - y))

            surface.blit(gradient_surface, (self.rect.left, self.rect.bottom - indicator_height))

            throttle_text = font.render(f"Throttle: {self.throttle_percent}%", True, (0, 0, 0))
            surface.blit(throttle_text, (self.rect.left, self.rect.bottom + 10))

class BrakePedal(Control):
    def __init__(self, pos, scale):
        super().__init__("images/brakePedal.png", pos, scale)

    def press(self):
        print("brake")

# Instantiate controls
wheel = Wheel((0.2675 * SCREEN_DIM[0], 0.4733 * SCREEN_DIM[1]),
              (int(0.375 * SCREEN_DIM[0]), int((2 / 3) * SCREEN_DIM[1])))

gas_pedal = GasPedal((0.6325 * SCREEN_DIM[0], 0.51 * SCREEN_DIM[1]),
                     (int(0.14 * SCREEN_DIM[0]), int(0.52 * SCREEN_DIM[1])))

brake_pedal = BrakePedal((0.845 * SCREEN_DIM[0], 0.625 * SCREEN_DIM[1]),
                         (int(0.25 * SCREEN_DIM[0]), int(0.25 * SCREEN_DIM[1])))

running = True
def display_warning():
    warning_text = font.render("Do not use this if nutting", True, (255, 0, 0))  # Red text
    screen.blit(warning_text, (SCREEN_DIM[0] // 2 - warning_text.get_width() // 2, 10))

# Main event loop
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
                brake_pedal.press()

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            wheel.dragging = False
            gas_pedal.release()

        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            if wheel.dragging:
                wheel.update_rotation(mouse_pos)
            if gas_pedal.throttling:
                gas_pedal.update_throttle(mouse_pos)

    if not wheel.dragging:
        wheel.return_to_center()

    screen.fill(BACKGROUND_COLOR)
    wheel.draw(screen)
    gas_pedal.draw(screen)
    brake_pedal.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()