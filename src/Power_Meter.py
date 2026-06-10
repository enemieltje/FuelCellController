from lib.ina226 import INA226
from Database import Database
from Sensor import Sensor
import logging

logger = logging.getLogger(__name__)


class Power_Meter(Sensor):
    """INA226 power monitor.

    Each physical INA226 produces three database sensor values: power, voltage,
    and current. The first sensor id is passed in, and the next two ids are used
    for voltage and current.
    """

    address = 0x41

    def __init__(self, sensor_id, address=0x41):
        self.sensor_id = sensor_id
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
        except Exception:
            logger.warning("Could not find INA226 %s", self.address)

    def get_power(self):
        try:
            return self.ina.power() / 1000.0
        except Exception:
            logger.warning(
                "INA226 %s disconnected, attempting reconnect", self.address)
            self.connect()
            return 0

    def get_current(self):
        try:
            return self.ina.current() / 1000.0
        except Exception:
            logger.warning(
                "INA226 %s disconnected, attempting reconnect", self.address)
            self.connect()
            return 0

    def get_voltage(self):
        try:
            return self.ina.voltage()
        except Exception:
            logger.warning(
                "INA226 %s disconnected, attempting reconnect", self.address)
            self.connect()
            return 0
