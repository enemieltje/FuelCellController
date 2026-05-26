import threading
import time
from Database import Database
import logging

logger = logging.getLogger(__name__)

class Sensor:

    def __init__(self, sensor_id):
        self.sensor_event = threading.Event()
        self.thread = threading.Thread(target=self.worker, daemon=True)
        self.sensor_id = sensor_id
        self.running = False
        self.value = 0
        self.interval = 1000
        self.start()

    def start(self):
        logger.debug(f"Sensor {self.sensor_id} starting")
        self.running = True
        self.thread.start()

    def stop(self):
        logger.debug(f"Sensor {self.sensor_id} stopping")
        self.running = False
        self.thread.join()

    def worker(self):
        while self.running:
            self.value = self.get_value()
            self.save_data()
            time.sleep(self.interval/1000)

    def get_value(self):
        logger.warn(f"Sensor {self.sensor_id} get_value not implemented")
        return 0

    def save_data(self):
        Database.insert(self.sensor_id, self.value)
