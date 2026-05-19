from lib.ADS1115 import ADS1115
import logging
ADS1115_REG_CONFIG_PGA_6_144V        = 0x00 # 6.144V range = Gain 2/3
ADS1115_REG_CONFIG_PGA_4_096V        = 0x02 # 4.096V range = Gain 1
ADS1115_REG_CONFIG_PGA_2_048V        = 0x04 # 2.048V range = Gain 2 (default)
ADS1115_REG_CONFIG_PGA_1_024V        = 0x06 # 1.024V range = Gain 4
ADS1115_REG_CONFIG_PGA_0_512V        = 0x08 # 0.512V range = Gain 8
ADS1115_REG_CONFIG_PGA_0_256V        = 0x0A # 0.256V range = Gain 16

logger = logging.getLogger(__name__)

class Analog_Pins:

    def __init__(self, addr=0x48):
        self.ads = ADS1115()
        self.ads.set_addr_ADS1115(addr)
        self.setGain()

    def setGain(self, gain=ADS1115_REG_CONFIG_PGA_6_144V):
        self.ads.set_gain(gain)

    def read(self, channel):
        try:
            return self.ads.read_voltage(channel)
        except:
            logger.warn("Could not find Analog Pins")
            return 0


# while True :
#     #Set the IIC address
#     #Sets the gain and input voltage range.
#     #Get the Digital Value of Analog of selected channel
#     adc0 = ads1115.read_voltage(0)
#     time.sleep(0.2)
#     adc1 = ads1115.read_voltage(1)
#     time.sleep(0.2)
#     adc2 = ads1115.read_voltage(2)
#     time.sleep(0.2)
#     adc3 = ads1115.read_voltage(3)
#     print "A0:%dmV A1:%dmV A2:%dmV A3:%dmV"%(adc0['r'],adc1['r'],adc2['r'],adc3['r'])
