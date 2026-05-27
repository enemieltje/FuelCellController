from Power_Meter import Power_Meter
from Database import SENSOR_ID
from Sensor import Sensor
import logging

logger = logging.getLogger(__name__)

LOW_VOLTAGE = 3.6
HIGH_VOLTAGE = 4.2
# Non-linear
LIPO_TABLE = [
    (4.20, 100),
    (4.15, 95),
    (4.11, 90),
    (4.08, 85),
    (4.02, 80),
    (3.98, 75),
    (3.95, 70),
    (3.91, 65),
    (3.87, 60),
    (3.85, 55),
    (3.84, 50),
    (3.82, 45),
    (3.80, 40),
    (3.79, 35),
    (3.77, 30),
    (3.75, 25),
    (3.73, 20),
    (3.71, 15),
    (3.69, 10),
    (3.61, 5),
    (3.00, 0),
]


class Battery:
    def __init__(self, analog_pins, channel=1):
        self.analog_pins = analog_pins
        self.channel = channel
        self.power_meter = Power_Meter(SENSOR_ID.BATTERY_POWER, 0x41)
        self.soc_sensor = Sensor(SENSOR_ID.BATTERY_SOC)

        def get_value():
            return self.get_percentage()
        self.soc_sensor.get_value = get_value

    def stop(self):
        self.power_meter.stop()
        self.soc_sensor.stop()

    def read_voltage(self):
        voltage = self.analog_pins.read(self.channel)
        return voltage

    def read_average(self, samples=10):
        return sum(self.read_voltage() for _ in range(samples)) / samples

    def get_percentage(self):
        voltage = self.read_voltage()

        # Clamp range
        if voltage >= 4.20:
            return 100.0
        if voltage <= 3.00:
            return 0.0

        # Find interval for interpolation
        for i in range(len(LIPO_TABLE) - 1):
            v1, soc1 = LIPO_TABLE[i]
            v2, soc2 = LIPO_TABLE[i + 1]

            if v1 >= voltage >= v2:
                # Linear interpolation
                ratio = (voltage - v2) / (v1 - v2)
                soc = soc2 + ratio * (soc1 - soc2)
                soc = round(soc, 1)
                logger.debug(f"Battery at {soc}% ({voltage} V)")
                return soc

        logger.debug(f"Battery disconnected")
        return None

    def get_power():
        Battery.power_meter.get_power()
