import statistics
from Config import Config
from lib.hx711 import HX711
import logging
import time

logger = logging.getLogger(__name__)


class Load_Cell():

    def _parse(value):
        lowValue = Config.getLoadcell('lowValue')
        lowWeight = Config.getLoadcell('lowWeight')
        highValue = Config.getLoadcell('highValue')
        highWeight = Config.getLoadcell('highWeight')
        return (value - lowValue) * (highWeight - lowWeight) / (highValue - lowValue) + lowWeight

    def start():
        logger.debug('Start')
        # Loadcell.hx = HX711(5, 6)
        Load_Cell.hx = HX711(dout_pin=5, pd_sck_pin=6, gain=128, channel='A')
        Load_Cell.reset()

    def reset():
        logger.debug("Reset")
        result = Load_Cell.hx.reset()		# Before we start, reset the hx711 ( not necessary)
        if result:			# you can check if the reset was successful
            logger.info('Ready to use')
        else:
            logger.warn('not ready')

    def print():
        logger.debug('Print')
        data = Load_Cell.hx.get_raw_data(5)

        if data != False:  # always check if you get correct value or only False
            logger.info('Raw data: ' + str(data) + "\n")
        else:
            logger.warn('invalid data')

    def read_raw():
        logger.debug('Read')
        data = Load_Cell.hx.get_raw_data()
        logger.debug(data)

        if data != False and len(data) > 1:
            return int(statistics.mean(data))

        logger.warn('invalid data')

    def read_parsed():
        return round(Load_Cell._parse(Load_Cell.read_raw()), 3)

    def config_low():
        lowValue = Load_Cell.readRaw()
        Config.setLoadcell('lowValue', str(lowValue))

    def config_high():
        highValue = Load_Cell.readRaw()
        Config.setLoadcell('highValue', str(highValue))

    def get_high_weight():
        return Config.getLoadcell('highWeight')

    def set_high_weight(highWeight):
        Config.setLoadcell('highWeight', str(highWeight))
