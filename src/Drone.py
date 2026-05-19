from Load_Cell import Load_Cell
from Power_Meter import Power_Meter
import gpiozero

class Drone:
    def start():
        Load_Cell.start()
        Drone.power_meter = Power_Meter(0x43)
        Drone.throttle = gpiozero.PWMOutputDevice(pin=12)

    def get_power():
        return Drone.power_meter.get_power()

    def get_thrust():
        return Load_Cell.read_parsed()

    def set_throttle(value):
        Drone.throttle.value = value

