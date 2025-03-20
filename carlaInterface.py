import sys
import carla
import prototypeUI
import threading
import time

client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()

print("Connected to Carla. Current map:", world.get_map().name)

def clear_vehicles():
    actors = world.get_actors().filter('*vehicle*')
    client.apply_batch([carla.command.DestroyActor(x) for x in actors])

def spawn_vehicle():
    blueprint_library = world.get_blueprint_library()
    car_bp = blueprint_library.filter('vehicle.*')[0]
    spawn_points = world.get_map().get_spawn_points()
    vehicle = None
    for spawn_point in spawn_points:
        vehicle = world.try_spawn_actor(car_bp, spawn_point)
        if vehicle:
            print(f'Spawned successfully at {spawn_point}')
            break
    if vehicle is None:
        raise RuntimeError('Could not spawn vehicle')
    return vehicle

def set_camera(vehicle):
    spectator = world.get_spectator()
    transform = vehicle.get_transform()
    cockpit_offset = carla.Location(x=0.5, z=1.2)
    spectator.set_transform(carla.Transform(
        transform.location + cockpit_offset,
        transform.rotation
    ))

# Start pygame UI clearly in parallel
ui_thread = threading.Thread(target=prototypeUI.main, daemon=True)
ui_thread.start()

clear_vehicles()
vehicle = spawn_vehicle()
set_camera(vehicle)

carlaControl = carla.VehicleControl()

try:
    while True:
        # Access UI values clearly via exposed method
        wheel_angle, gas_throttle, brake_throttle = prototypeUI.get_controls()

        # Map wheel angle to CARLA steer (-450 to 450 degrees -> -1 to 1 range)
        max_angle = 450
        steer = max(min(wheel_angle / max_angle, 1.0), -1.0)

        carlaControl.steer = steer
        carlaControl.throttle = max(min(gas_throttle, 1.0), 0.0)
        carlaControl.brake = max(min(brake_throttle, 1.0), 0.0)

        vehicle.apply_control(carlaControl)

        time.sleep(0.05)  # ~20 Hz control loop for smoothness clearly

except KeyboardInterrupt:
    print("Exiting.")

finally:
    vehicle.destroy()
