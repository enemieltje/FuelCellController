import threading
import time
from Database import Database
import logging

logger = logging.getLogger(__name__)


class Sensor:
    """Base class for sensors that periodically save values to the database.

    Subclasses normally override either ``get_value`` for a single value or
    ``save_data`` when one physical device produces several measurements.
    """

    def __init__(self, sensor_id, interval_ms=100):
        self.sensor_event = threading.Event()
        self.thread = threading.Thread(target=self.worker, daemon=True)
        self.sensor_id = sensor_id
        self.running = False
        self.value = 0
        self.interval = interval_ms
        self.start()

    def start(self):
        logger.debug(f"Sensor {self.sensor_id} starting")
        self.running = True
        self.thread.start()

    def stop(self):
        logger.debug(f"Sensor {self.sensor_id} stopping")
        self.running = False
        if self.thread.is_alive():
            self.thread.join()

    def worker(self):
        """Poll the sensor until stopped.

        The interval is stored in milliseconds because that is easier to read
        when comparing it to hardware sample rates.
        """
        while self.running:
            self.value = self.get_value()
            self.save_data()
            time.sleep(self.interval / 1000)

    def get_value(self):
        """Return a single sensor reading.

        The base class returns 0 so that simple placeholder sensors are safe
        while hardware is disconnected during local development.
        """
        return 0

    def save_data(self):
        Database.insert(self.sensor_id, self.value)
