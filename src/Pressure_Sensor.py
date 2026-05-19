class Pressure_Sensor:

    def __init__(self, analog_pins, channel=0):
        self.analog_pins = analog_pins
        self.channel = channel


    def read_pressure(self):
        voltage = self.analog_pins.read(self.channel)
        current = voltage / 120
        pressure = ((current - 0.004) / (0.02 - 0.004)) * 10
        return pressure


    def read_average(self, samples=10):
        return sum(self.read_pressure() for _ in range(samples)) / samples
