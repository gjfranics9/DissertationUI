import pygame
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_DIM = (1280, 720)
BACKGROUND_COLOR = (0x93, 0x95, 0x97)
FPS = 60

# Set up display
screen = pygame.display.set_mode(SCREEN_DIM, pygame.SRCALPHA)
clock = pygame.time.Clock()
font = pygame.font.Font("freesansbold.ttf", 24)

# Base class for controls (steering wheel, pedals, etc.)
class Control:
    def __init__(self, img_path, pos, scale):
        original_image = pygame.image.load(img_path).convert_alpha()
        self.original_image = pygame.transform.scale(original_image, scale)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=pos)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def press(self):
        pass  # To be implemented by subclasses

# Steering Wheel class with rotation logic
class Wheel(Control):
    def __init__(self, pos, scale):
        super().__init__("images/steeringWheel.png", pos, scale)
        self.angle = 0
        self.dragging = False
        self.initial_mouse_angle = 0
        self.initial_wheel_angle = 0
        self.max_rotation_speed = 6.25  # Maximum degrees per frame

    def rotate(self, angle):
        # Limit rotation angle to ±90 degrees
        target_angle = max(-90, min(90, angle))
        angle_difference = target_angle - self.angle

        # Apply maximum rotation speed limit
        if abs(angle_difference) > self.max_rotation_speed:
            angle_difference = math.copysign(self.max_rotation_speed, angle_difference)

        self.angle += angle_difference
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def calculate_angle(self, mouse_pos):
        dx = mouse_pos[0] - self.rect.centerx
        dy = mouse_pos[1] - self.rect.centery
        return math.degrees(math.atan2(-dy, dx))

    def start_drag(self, mouse_pos):
        self.dragging = True
        self.initial_mouse_angle = self.calculate_angle(mouse_pos)
        self.initial_wheel_angle = self.angle

    def update_rotation(self, mouse_pos):
        current_mouse_angle = self.calculate_angle(mouse_pos)
        angle_difference = current_mouse_angle - self.initial_mouse_angle
        desired_angle = self.initial_wheel_angle + angle_difference
        self.rotate(desired_angle)

    def return_to_center(self):
        # Smoothly recenter the steering wheel
        recenter_speed = 3.6
        if abs(self.angle) > 1:
            self.rotate(self.angle - recenter_speed * math.copysign(1, self.angle))
        else:
            self.rotate(0)

    def press(self):
        print("wheel")

class GasPedal(Control):
    def __init__(self, pos, scale):
        super().__init__("images/gasPedal.png", pos, scale)

    def press(self):
        print("gas")


class BrakePedal(Control):
    def __init__(self, pos, scale):
        super().__init__("images/brakePedal.png", pos, scale)

    def press(self):
        print("brake")

# Main Function
def main():
    # Instantiate control objects with corrected center-based positions
    wheel = Wheel((0.2675 * SCREEN_DIM[0], 0.4733 * SCREEN_DIM[1]),
                  (int(0.375 * SCREEN_DIM[0]), int((2 / 3) * SCREEN_DIM[1])))

    gas_pedal = GasPedal((0.6325 * SCREEN_DIM[0], 0.51 * SCREEN_DIM[1]),
                         (int(0.14 * SCREEN_DIM[0]), int(0.52 * SCREEN_DIM[1])))

    brake_pedal = BrakePedal((0.845 * SCREEN_DIM[0], 0.625 * SCREEN_DIM[1]),
                             (int(0.25 * SCREEN_DIM[0]), int(0.25 * SCREEN_DIM[1])))

    running = True

    # Main game loop
    while running:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if wheel.rect.collidepoint(mouse_pos):
                    wheel.start_drag(mouse_pos)
                elif gas_pedal.rect.collidepoint(mouse_pos):
                    gas_pedal.press()
                elif brake_pedal.rect.collidepoint(mouse_pos):
                    brake_pedal.press()

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                wheel.dragging = False

            elif event.type == pygame.MOUSEMOTION and wheel.dragging:
                wheel.update_rotation(event.pos)

        # Automatically return wheel to center if not being dragged
        if not wheel.dragging:
            wheel.return_to_center()

        # Drawing section
        screen.fill(BACKGROUND_COLOR)
        wheel.draw(screen)
        gas_pedal.draw(screen)
        brake_pedal.draw(screen)

        # Display cursor coordinates
        mouse_pos = pygame.mouse.get_pos()
        mouse_coords = font.render(f"{mouse_pos[0]}, {mouse_pos[1]}", True, (0, 0, 0))
        screen.blit(mouse_coords, (0, 0))

        # Update display
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

# Run main loop
if __name__ == "__main__":
    main()
