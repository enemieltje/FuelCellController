import statistics
from config import Config
from lib.hx711 import HX711
import logging
import time

logger = logging.getLogger(__name__)


class Loadcell():

    def _parse(value):
        lowValue = Config.getLoadcell('lowValue')
        lowWeight = Config.getLoadcell('lowWeight')
        highValue = Config.getLoadcell('highValue')
        highWeight = Config.getLoadcell('highWeight')
        return (value - lowValue) * (highWeight - lowWeight) / (highValue - lowValue) + lowWeight

    def start():
        logger.debug('Start')
        # Loadcell.hx = HX711(5, 6)
        Loadcell.hx = HX711(dout_pin=5, pd_sck_pin=6, gain=128, channel='A')
        Loadcell.reset()

    def reset():
        logger.debug("Reset")
        result = Loadcell.hx.reset()		# Before we start, reset the hx711 ( not necessary)
        if result:			# you can check if the reset was successful
            logger.info('Ready to use')
        else:
            logger.warn('not ready')

    def print():
        logger.debug('Print')
        data = Loadcell.hx.get_raw_data(5)

        if data != False:  # always check if you get correct value or only False
            logger.info('Raw data: ' + str(data) + "\n")
        else:
            logger.warn('invalid data')

    def readRaw():
        logger.debug('Read')
        data = Loadcell.hx.get_raw_data()
        logger.debug(data)

        if data != False and len(data) > 1:
            return int(statistics.mean(data))

        logger.warn('invalid data')

    def readParsed():
        return round(Loadcell._parse(Loadcell.readRaw()), 3)

    def configLow():
        lowValue = Loadcell.readRaw()
        Config.setLoadcell('lowValue', str(lowValue))

    def configHigh():
        highValue = Loadcell.readRaw()
        Config.setLoadcell('highValue', str(highValue))

    def getHighWeight():
        return Config.getLoadcell('highWeight')

    def setHighWeight(highWeight):
        Config.setLoadcell('highWeight', str(highWeight))
