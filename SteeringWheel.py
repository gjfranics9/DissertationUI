import pygame
import math
from Control import Control

# Initialize Pygame
pygame.init()

# Steering wheel class with rotation and recentering
class Wheel(Control):
    def __init__(self, pos, scale):
        super().__init__("images/steeringWheel.png", pos, scale)
        self.angle = 0 # Current rotation angle
        self.dragging = False # Dragging state
        self.initial_mouse_angle = 0 # Initial angle when dragging starts
        self.initial_wheel_angle = 0 # Initial angle when dragging starts
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

    def getAngle(self):
        """Return current wheel angle."""
        print(self.angle/90)
        return max(min(self.angle/90, 1), -1)

    def return_to_center(self):
        """Gradually return wheel to center when not in use."""
        if abs(self.angle) > 1:
            self.rotate(self.angle - 2 * math.copysign(1, self.angle))
        else:
            self.rotate(0)