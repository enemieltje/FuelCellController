from lib.ina226 import INA226
from Database import Database
import logging

logger = logging.getLogger(__name__)

class Power_Meter():
    address=0.41

    def __init__(self, address=0x41):
        print()
        logger.debug(f'Start INA226 {self.address}')
        self.address = address
        self.connect()

    def connect(self):
        try:
            self.ina = INA226(address=self.address, max_expected_amps=25, log_level=logging.DEBUG)
            self.ina.configure()
            logger.info(f"INA226 {self.address} Connected!")
        except:
            logger.warn(f"Could not find INA226 {self.address}")


    def get_power(self):
        try:
            return self.ina.power() * 1000.0
        except:
            print()
            logger.warn(f"INA226 {self.address} disconnected, attempting reconnect")
            self.connect()
            return 0


    def get_current(self):
        try:
            return self.ina.current() * 1000.0
        except:
            print()
            logger.warn(f"INA226 {self.address} disconnected, attempting reconnect")
            self.connect()
            return 0



    def get_voltage(self):
        try:
            return self.ina.voltage()
        except:
            print()
            logger.warn(f"INA226 {self.address} disconnected, attempting reconnect")
            self.connect()
            return 0

