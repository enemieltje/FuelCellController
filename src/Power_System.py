from Power_Meter import Power_Meter
from Analog_Pins import Analog_Pins
from Pressure_Sensor import Pressure_Sensor
from Load_Cell import Load_Cell
from Battery import Battery
import gpiozero
import logging
from Drone import Drone
from Database import Database, SENSOR_ID

logger = logging.getLogger(__name__)

class Power_System:

    def start():
        Power_System.analog_pins = Analog_Pins()
        Power_System.pressure_sensor = Pressure_Sensor(Power_System.analog_pins)
        Power_System.battery = Battery(Power_System.analog_pins)

        Power_System.fc_power = Power_Meter(SENSOR_ID.FUELCELL_POWER , 0x40)

        Power_System.fuel_cell = gpiozero.OutputDevice(13, active_high=False)
        Power_System.relay = gpiozero.OutputDevice(27, active_high=False)
        Power_System.save_measurement()
        # Database.get_run()
        Database.get_csv()
        logger.debug(f"Battery SOC: {Database.get_latest(SENSOR_ID.BATTERY_SOC)}")

    def stop():
        Power_System.battery.stop()
        Power_System.fc_power.stop()
        Power_System.pressure_sensor.stop()


    def enable():
        Power_System.fuel_cell.on()


    def disable():
        Power_System.fuel_cell.off()

    def save_measurement():
        logger.debug("Saving Sensor Data to Database")
        # fc = Power_System.fc_power
        # battery = Power_System.battery.power_meter
        # drone = Drone.power_meter
        # Database.insert(
        #     fc.get_power(),
        #     fc.get_voltage(),
        #     fc.get_current(),
        #     battery.get_power(),
        #     battery.get_voltage(),
        #     battery.get_current(),
        #     drone.get_power(),
        #     drone.get_voltage(),
        #     drone.get_current(),
        #     Power_System.battery.get_percentage(),
        #     Power_System.pressure_sensor.read_average(),
        #     Load_Cell.read_parsed(),
        # )
        Database.insert(SENSOR_ID.BATTERY_SOC, Power_System.battery.get_percentage())
        Database.insert(SENSOR_ID.PRESSURE, Power_System.pressure_sensor.read_pressure())
        Database.insert(SENSOR_ID.THRUST, Load_Cell.read_parsed())
