from lib.ina226 import INA226
from Database import Database
from Sensor import Sensor
import logging

logger = logging.getLogger(__name__)


class Power_Meter(Sensor):
    address = 0.41

    def __init__(self, sensor_id, address=0x41):
        self.sensor_id = sensor_id
        print()
        self.address = address
        logger.debug(f'Start INA226 {self.address}')
        self.connect()
        Sensor.__init__(self, sensor_id)

    def save_data(self):
        Database.insert(self.sensor_id, self.get_power())
        Database.insert(self.sensor_id + 1, self.get_voltage())
        Database.insert(self.sensor_id + 2, self.get_current())

    def connect(self):
        try:
            self.ina = INA226(address=self.address,
                              max_expected_amps=25, log_level=logging.WARNING)
            self.ina.configure()
            logger.info(f"INA226 {self.address} Connected!")
        except:
            logger.warn(f"Could not find INA226 {self.address}")

    def get_power(self):
        try:
            return self.ina.power() / 1000.0
        except:
            print()
            logger.warn(
                f"INA226 {self.address} disconnected, attempting reconnect")
            self.connect()
            return 0

    def get_current(self):
        try:
            return self.ina.current() / 1000.0
        except:
            print()
            logger.warn(
                f"INA226 {self.address} disconnected, attempting reconnect")
            self.connect()
            return 0

    def get_voltage(self):
        try:
            return self.ina.voltage()
        except:
            print()
            logger.warn(
                f"INA226 {self.address} disconnected, attempting reconnect")
            self.connect()
            return 0
