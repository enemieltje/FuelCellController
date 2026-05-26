import logging
from Database import Database
from Sensor import Sensor

logger = logging.getLogger(__name__)

class Pressure_Sensor(Sensor):

    def __init__(self, analog_pins, channel=0):
        self.analog_pins = analog_pins
        self.channel = channel
        super().__init__(Database.PRESSURE)

    def get_value(self):
        return self.read_pressure()


    def read_pressure(self):
        voltage = self.analog_pins.read(self.channel)
        current = voltage / 120.0
        pressure = ((current - 0.004) / (0.02 - 0.004)) * 10.0
        logger.debug(f"Pressure: {pressure} bar ({voltage} V)")
        return pressure


    def read_average(self, samples=10):
        return sum(self.read_pressure() for _ in range(samples)) / samples
