from Power_Meter import Power_Meter
from Analog_Pins import Analog_Pins
from Pressure_Sensor import Pressure_Sensor
from Battery import Battery
import gpiozero
import logging
from Database import SENSOR_ID

logger = logging.getLogger(__name__)


class Power_System:

    def start():
        Power_System.analog_pins = Analog_Pins()
        Power_System.pressure_sensor = Pressure_Sensor(
            Power_System.analog_pins)
        Power_System.battery = Battery(Power_System.analog_pins)

        Power_System.fc_power = Power_Meter(SENSOR_ID.FUELCELL_POWER, 0x40)

        Power_System.fuel_cell = gpiozero.OutputDevice(13, active_high=False)
        Power_System.relay = gpiozero.OutputDevice(27, active_high=False)

    def stop():
        Power_System.battery.stop()
        Power_System.fc_power.stop()
        Power_System.pressure_sensor.stop()

    def enable():
        Power_System.fuel_cell.on()

    def disable():
        Power_System.fuel_cell.off()
