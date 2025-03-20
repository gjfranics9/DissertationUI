import sys
import carla
import prototypeUI
import threading

client = carla.Client('localhost', 2000)
client.set_timeout(10.0)

world = client.get_world()
print("Connected to Carla. Current map: ", world.get_map().name)

def clear_vehicles():
    #clear map
    actors = world.get_actors().filter('*vehicle*')
    client.apply_batch([carla.command.DestroyActor(x) for x in actors])

def spawn_vehicle():
    #spawn vehicle
    blueprint_library = world.get_blueprint_library()
    car_bp = blueprint_library.filter('vehicle.*')[0]
    spawn_points = world.get_map().get_spawn_points()
    for spawn_point in spawn_points:
        vehicle = world.try_spawn_actor(car_bp, spawn_point)
        if vehicle:
            print(f'Spawned succesfully at {spawn_point}')
            break
    if vehicle is None:
        print('Could not spawn vehicle')
        raise RuntimeError('Could not spawn vehicle')
    return vehicle

def set_camera():
#Camera
    spectator = world.get_spectator()
    transform = vehicle.get_transform()

    cockpit_offset = carla.Location(x=0.5, z=1.2)
    spectator.set_transform(carla.Transform(
        transform.location + cockpit_offset,
        transform.rotation
    ))

ui_thread = threading.Thread(target=prototypeUI.main, daemon=True)
ui_thread.start()

carlaControl = carla.VehicleControl()

clear_vehicles()
vehicle = spawn_vehicle()
set_camera()
try:
    while True:
        carlaControl.throttle = prototypeUI.gas_pedal.throttle
        carlaControl.brake = prototypeUI.brake_pedal.throttle
        carlaControl.steer = prototypeUI.wheel.rotation
        vehicle.apply_control(carlaControl)
finally:
    vehicle.destroy()