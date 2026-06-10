import logging
from Database import SENSOR_ID, Database
from Sensor import Sensor
import propar

logger = logging.getLogger(__name__)


class Pressure_Sensor(Sensor):
    """Reads CGG pressure locally and Bronkhorst flow-controller values."""

    bh: propar.instrument

    def __init__(self, analog_pins, channel=0):
        self.analog_pins = analog_pins
        self.channel = channel
        self.bh = None
        self.connect_bronkhorst()

        super().__init__(SENSOR_ID.CGG_PRESSURE, interval_ms=40)

    def connect_bronkhorst(self):
        try:
            self.bh = propar.instrument('/dev/ttyACM0')
            # set control function to Downstream Pressure
            self.bh.writeParameter(432, 2)
            # Set downstream pressure setpoint
            self.bh.writeParameter(206, 1.4, channel=3)
            # fluid_type = self.bh.readParameter(206, channel=3)
            # logger.info(f'Setpoint: {fluid_type} bar')
            # fluid_type = self.bh.readParameter(432)
            # logger.info(f'Control Mode: {fluid_type}')
            self.use_hydrogen()
        except Exception:
            logger.warning("Bronkhorst not found")

    def get_fluid_type(self):
        if not self.bh:
            return 0

        return self.bh.readParameter(25)

    def set_fluid_type(self, fluid_index):
        if not self.bh:
            return 0
        self.bh.writeParameter(24, fluid_index)

        fluid_type = self.get_fluid_type()
        logger.info(f'Set fluid to {fluid_type} ({fluid_index})')
        return fluid_type

    def use_hydrogen(self):
        return self.set_fluid_type(3)

    def use_air(self):
        return self.set_fluid_type(0)

    def save_data(self):
        Database.insert(self.sensor_id, self.read_pressure())
        Database.insert(self.sensor_id + 1, self.read_upstream())
        Database.insert(self.sensor_id + 2, self.read_downstream())
        Database.insert(self.sensor_id + 3, self.read_flow())

    def read_pressure(self):
        voltage = self.analog_pins.read(self.channel)
        # The pressure transducer outputs 4-20 mA. The 120 ohm resistor converts
        # that current into a voltage that the ADS1115 can measure.
        current = voltage / 120.0
        pressure = ((current - 0.004) / (0.02 - 0.004)) * 10.0
        # Clamp and convert to absolute pressure (+1 bar)
        pressure = max(0, min(pressure, 10)) + 1.0
        # logger.debug(f"Pressure: {pressure} bar ({voltage} V)")
        return pressure

    def read_average(self, samples=10):
        return sum(self.read_pressure() for _ in range(samples)) / samples

    def read_upstream(self):
        if not self.bh:
            return 0
        pressure = self.bh.readParameter(205, channel=2)
        # logger.debug(f"Upstream Pressure: {pressure} bar")
        return pressure

    def read_downstream(self):
        if not self.bh:
            return 0
        pressure = self.bh.readParameter(205, channel=3)
        # logger.debug(f"Downstream Pressure: {pressure} bar")
        return pressure

    def read_flow(self):
        if not self.bh:
            return 0
        flow = self.bh.readParameter(205, channel=1)
        # logger.debug(f"Flow: {flow}")
        return flow
