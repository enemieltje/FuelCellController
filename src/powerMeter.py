from lib.ina226 import INA226
import logging

logger = logging.getLogger(__name__)

class PowerMeter():
    busnum=1

    def __init__(self, busnum=1):
        logger.debug('Start')
        self.busnum = busnum
        self.connect()

    def connect(self):
        try:
            self.ina = INA226(busnum=busnum, max_expected_amps=25, log_level=logging.DEBUG)
            self.ina.configure()
        except:
            logger.warn("Could not find INA226")
