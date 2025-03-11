import pygame
import math

# Pygame setup
pygame.init()
screen_dim = (1280, 720)
screen = pygame.display.set_mode(screen_dim, pygame.SRCALPHA)
clock = pygame.time.Clock()
font = pygame.font.Font("freesansbold.ttf", 24)

# Base class for controls (wheel, pedals, etc.)
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
    def return_to_center(self):
    # Smoothly return the wheel to the center position
        if self.angle > 1:
            self.angle -= 2  # Adjust speed of return as desired
        elif self.angle < -1:
            self.angle += 2
        else:
            self.angle = 0

        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)


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


# Instantiate objects with original multipliers
wheel = Wheel((0.08 * screen_dim[0], 0.14 * screen_dim[1]), (int(0.375 * screen_dim[0]), int((2 / 3) * screen_dim[1])))
gas_pedal = GasPedal((0.5625 * screen_dim[0], 0.25 * screen_dim[1]), (int(0.14 * screen_dim[0]), int(0.52 * screen_dim[1])))
brake_pedal = BrakePedal((0.72 * screen_dim[0], 0.5 * screen_dim[1]), (int(0.25 * screen_dim[0]), int(0.25 * screen_dim[1])))

running = True

# Main loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos

            if wheel.rect.collidepoint(mouse_pos):
                wheel.dragging = True
            elif gas_pedal.rect.collidepoint(mouse_pos):
                gas_pedal.press()
            elif brake_pedal.rect.collidepoint(mouse_pos):
                brake_pedal.press()

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            wheel.dragging = False

        if event.type == pygame.MOUSEMOTION and wheel.dragging:
            wheel.update_rotation(event.pos)

    # Fill background using hex color (0x93, 0x95, 0x97)
    screen.fill((0x93, 0x95, 0x97))

    # Draw controls
    wheel.draw(screen)
    gas_pedal.draw(screen)
    brake_pedal.draw(screen)

    # Retrieve and display cursor position
    mouse_pos = pygame.mouse.get_pos()
    mouse_coords = font.render(f"{mouse_pos[0]}, {mouse_pos[1]}", True, (0, 0, 0))
    screen.blit(mouse_coords, (0, 0))
    
    # Returns wheel to middle
    if not wheel.dragging:
        wheel.return_to_center()


    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
