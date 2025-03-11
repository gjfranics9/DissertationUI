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
        self.rect = self.image.get_rect(topleft=pos)

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

    def rotate(self, angle):
        # Limit rotation angle to ±90 degrees
        self.angle = max(-90, min(90, angle))
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update_rotation(self, mouse_pos):
        dx, dy = mouse_pos[0] - self.rect.centerx, mouse_pos[1] - self.rect.centery
        angle = math.degrees(math.atan2(-dy, dx))
        self.rotate(angle)

    def press(self):
        print("wheel")

    def return_to_center(self):
        # Smoothly return wheel to center position
        if self.angle > 1:
            self.rotate(self.angle - 2)
        elif self.angle < -1:
            self.rotate(self.angle + 2)
        else:
            self.rotate(0)


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


def main():
    # Instantiate control objects with original multipliers
    wheel = Wheel((0.08 * SCREEN_DIM[0], 0.14 * SCREEN_DIM[1]), (int(0.375 * SCREEN_DIM[0]), int((2 / 3) * SCREEN_DIM[1])))
    gas_pedal = GasPedal((0.5625 * SCREEN_DIM[0], 0.25 * SCREEN_DIM[1]), (int(0.14 * SCREEN_DIM[0]), int(0.52 * SCREEN_DIM[1])))
    brake_pedal = BrakePedal((0.72 * SCREEN_DIM[0], 0.5 * SCREEN_DIM[1]), (int(0.25 * SCREEN_DIM[0]), int(0.25 * SCREEN_DIM[1])))

    running = True

    # Main loop
    while running:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos

                if wheel.rect.collidepoint(mouse_pos):
                    wheel.dragging = True
                elif gas_pedal.rect.collidepoint(mouse_pos):
                    gas_pedal.press()
                elif brake_pedal.rect.collidepoint(mouse_pos):
                    brake_pedal.press()

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                wheel.dragging = False

            elif event.type == pygame.MOUSEMOTION and wheel.dragging:
                wheel.update_rotation(event.pos)

        # Return wheel to center if not dragging
        if not wheel.dragging:
            wheel.return_to_center()

        # Drawing Section
        screen.fill(BACKGROUND_COLOR)

        wheel.draw(screen)
        gas_pedal.draw(screen)
        brake_pedal.draw(screen)

        # Display cursor position
        mouse_pos = pygame.mouse.get_pos()
        mouse_coords = font.render(f"{mouse_pos[0]}, {mouse_pos[1]}", True, (0, 0, 0))
        screen.blit(mouse_coords, (0, 0))

        # Update display and maintain FPS
        pygame.display.flip()
        clock.tick(FPS)

        # Return wheel to center smoothly
        if not wheel.dragging:
            wheel.return_to_center()

    pygame.quit()


# Run main loop
if __name__ == "__main__":
    main()