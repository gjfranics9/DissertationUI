import pygame

# Pygame setup
pygame.init()
screen_dim = (1280, 720)
screen = pygame.display.set_mode(screen_dim, pygame.SRCALPHA)
clock = pygame.time.Clock()

class Control:
    def __init__(self, img_path, pos, scale):
        original_image = pygame.image.load(img_path).convert_alpha()
        self.image = pygame.transform.scale(original_image, scale)
        self.rect = self.image.get_rect(topleft=pos)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def press(self):
        pass  # To be implemented by subclasses


class Wheel(Control):
    def __init__(self, pos, scale):
        super().__init__("images/steeringWheel.png", pos, scale)

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

            for control in [wheel, gas_pedal, brake_pedal]:
                if control.rect.collidepoint(mouse_pos):
                    control.press()

    # Fill background using hex color (0x93, 0x95, 0x97)
    screen.fill((0x93, 0x95, 0x97))

    # Draw controls
    wheel.draw(screen)
    gas_pedal.draw(screen)
    brake_pedal.draw(screen)

    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
