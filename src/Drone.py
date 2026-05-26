from Load_Cell import Load_Cell
from Power_Meter import Power_Meter
from Database import SENSOR_ID
from Sensor import Sensor
import gpiozero
import time
import logging


logger = logging.getLogger(__name__)

class Drone:
    def start():
        Load_Cell.start()
        Drone.power_meter = Power_Meter(SENSOR_ID.LOAD_POWER, 0x43)
        Drone.power = gpiozero.OutputDevice(pin=17, active_high=False)
        Drone.throttle = gpiozero.Servo(
            pin=19,
            min_pulse_width=0.001,   # 1 ms
            max_pulse_width=0.002    # 2 ms
        )

        def get_value():
            return Drone.throttle.value
        Drone.throttle_sensor = Sensor(SENSOR_ID.THROTTLE)
        Drone.throttle_sensor.get_value = get_value

    def stop():
        Load_Cell.stop()
        Drone.power_meter.stop()
        Drone.throttle_sensor.stop()
        Drone.set_throttle(0.0)
        Drone.throttle.detach()
        time.sleep(2)
        Drone.power.off()


    def arm():
        logger.info("Arming ESC")
        Drone.power.on()

        # minimum throttle
        Drone.set_throttle(0.0)

        time.sleep(3)

        logger.info("ESC armed")


    def calibrate():
        logger.info("Starting calibration")

        # full throttle
        Drone.set_throttle(1.0)

        time.sleep(1)
        Drone.power.on()
        time.sleep(5)

        # minimum throttle
        Drone.set_throttle(0.0)

        time.sleep(3)

        logger.info("Calibration complete")

    def get_power():
        return Drone.power_meter.get_power()

    def get_thrust():
        return Load_Cell.read_parsed()

    def set_throttle(value):
        value = max(0.0, min(1.0, value))
        value = (value * 2.0) - 1.0
        logger.info(f"Set throttle to {value}")
        Drone.throttle.value = value


