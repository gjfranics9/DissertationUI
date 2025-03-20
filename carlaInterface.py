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

def follow_vehicle(vehicle):
    """ Continuously update spectator camera to smoothly follow vehicle in cockpit view """
    spectator = world.get_spectator()

    # Cockpit camera offset (driver's seat perspective)
    cockpit_offset = carla.Location(x=0.5, y=0.0, z=1.2)

    while True:
        vehicle_transform = vehicle.get_transform()

        # Calculate camera position based on vehicle rotation
        camera_transform = carla.Transform(
            vehicle_transform.transform(cockpit_offset),
            vehicle_transform.rotation
        )

        spectator.set_transform(camera_transform)

        time.sleep(0.02)  # Higher frequency (~50Hz) for smoother updates


# Start pygame UI in parallel
ui_thread = threading.Thread(target=prototypeUI.main, daemon=True)
ui_thread.start()

clear_vehicles()
vehicle = spawn_vehicle()

# Start the camera-follow function in a separate thread
camera_thread = threading.Thread(target=follow_vehicle, args=(vehicle,), daemon=True)
camera_thread.start()

carlaControl = carla.VehicleControl()

try:
    while True:
        # Get steering, throttle, and brake from UI
        _, gas_throttle, brake_throttle = prototypeUI.get_controls()

        # Get steering angle directly (normalized)
        steer = prototypeUI.wheel.getAngle()

        # Apply controls to CARLA
        carlaControl.steer = steer
        carlaControl.throttle = max(min(gas_throttle, 1.0), 0.0)
        carlaControl.brake = max(min(brake_throttle, 1.0), 0.0)

        vehicle.apply_control(carlaControl)

        time.sleep(0.05)  # Run at ~20Hz for smooth updates

except KeyboardInterrupt:
    print("Exiting.")

finally:
    vehicle.destroy()
