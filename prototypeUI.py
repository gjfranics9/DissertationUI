# prototypeUI.py (modified to clearly expose UI elements)
import pygame
from SteeringWheel import Wheel
from GasPedal import GasPedal
from BrakePedal import BrakePedal

wheel = None
gas_pedal = None
brake_pedal = None

def main():
    global wheel, gas_pedal, brake_pedal

    pygame.init()
    SCREEN_DIM = (1280, 720)
    screen = pygame.display.set_mode(SCREEN_DIM)
    clock = pygame.time.Clock()
    FPS = 60

    wheel = Wheel((0.2675 * SCREEN_DIM[0], 0.4733 * SCREEN_DIM[1]),
                  (int(0.375 * SCREEN_DIM[0]), int((2 / 3) * SCREEN_DIM[1])))
    
    gas_pedal = GasPedal((0.6325 * SCREEN_DIM[0], 0.51 * SCREEN_DIM[1]),
                         (int(0.14 * SCREEN_DIM[0]), int(0.52 * SCREEN_DIM[1])))
    
    brake_pedal = BrakePedal((0.845 * SCREEN_DIM[0], 0.625 * SCREEN_DIM[1]),
                             (int(0.25 * SCREEN_DIM[0]), int(0.25 * SCREEN_DIM[1])))
    
    # Load and scale background image
    background = pygame.image.load("images/background.png")
    background = pygame.transform.scale(background, SCREEN_DIM)

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

            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                if wheel.dragging:
                    wheel.update_rotation(mouse_pos)
                if gas_pedal.throttling:
                    gas_pedal.update_throttle(mouse_pos)
                if brake_pedal.throttling:
                    brake_pedal.update_throttle(mouse_pos)

        if not wheel.dragging:
            wheel.return_to_center()

        screen.blit(background, (0, 0))
        wheel.draw(screen)
        gas_pedal.draw(screen)
        brake_pedal.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

# Expose getters clearly for external access
def get_controls():
    return wheel.getAngle(), gas_pedal.getThrottle(), brake_pedal.getThrottle()