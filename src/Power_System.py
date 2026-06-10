from Power_Meter import Power_Meter
from Analog_Pins import Analog_Pins
from Pressure_Sensor import Pressure_Sensor
from Battery import Battery
import gpiozero
import logging
from Database import SENSOR_ID

logger = logging.getLogger(__name__)


class Power_System:
    """Coordinates the fuel-cell-side hardware.

    The project uses class-level state here as a simple singleton. ``start``
    creates each hardware adapter once, and the web server calls ``enable`` and
    ``disable`` to switch the fuel cell relay.
    """

    def start():
        Power_System.analog_pins = Analog_Pins()
        Power_System.pressure_sensor = Pressure_Sensor(
            Power_System.analog_pins)
        Power_System.battery = Battery(Power_System.analog_pins)

        Power_System.fc_power = Power_Meter(SENSOR_ID.FUELCELL_POWER, 0x40)

        Power_System.fuel_cell = gpiozero.OutputDevice(27, active_high=True)
        # Power_System.relay = gpiozero.OutputDevice(27, active_high=False)

    def stop():
        for component_name in ("battery", "fc_power", "pressure_sensor"):
            component = getattr(Power_System, component_name, None)
            if component:
                component.stop()

        fuel_cell = getattr(Power_System, "fuel_cell", None)
        if fuel_cell:
            fuel_cell.off()

    def enable():
        Power_System.fuel_cell.on()

    def disable():
        Power_System.fuel_cell.off()
