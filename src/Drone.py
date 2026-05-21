from Load_Cell import Load_Cell
from Power_Meter import Power_Meter
import gpiozero
import time
import logging

logger = logging.getLogger(__name__)

class Drone:
    def start():
        Load_Cell.start()
        Drone.power_meter = Power_Meter(0x43)
        Drone.throttle = gpiozero.PWMOutputDevice(pin=19)
        Drone.power = gpiozero.OutputDevice(pin=27, active_high=False)

    def arm():
        Drone.power.off()
        time.sleep(3)
        Drone.set_throttle(1)
        Drone.power.on()
        time.sleep(3)
        Drone.set_throttle(0)

    def get_power():
        return Drone.power_meter.get_power()

    def get_thrust():
        return Load_Cell.read_parsed()

    def set_throttle(value):
        logger.info(f"Set throttle to {value}")
        Drone.throttle.value = value


