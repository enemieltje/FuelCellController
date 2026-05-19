from lib.ina226 import INA226
import logging

logger = logging.getLogger(__name__)

class Power_Meter():
    channel=0.41

    def __init__(self, channel=0x41):
        logger.debug('Start')
        self.channel = channel
        self.connect()

    def connect(self):
        try:
            self.ina = INA226(channel=self.channel, max_expected_amps=25, log_level=logging.DEBUG)
            self.ina.configure()
        except:
            logger.warn("Could not find INA226")


    def get_power(self):
        try:
            return self.ina.get_power()
        except:
            logger.warn("INA226 disconnected, attempting reconnect")
            self.connect()
            return 0


    def get_current(self):
        try:
            return self.ina.get_current()
        except:
            logger.warn("INA226 disconnected, attempting reconnect")
            self.connect()
            return 0



    def get_voltage(self):
        try:
            return self.ina.get_voltage()
        except:
            logger.warn("INA226 disconnected, attempting reconnect")
            self.connect()
            return 0
