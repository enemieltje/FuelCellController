import sqlite3
import logging
import pandas as pd
import threading
from datetime import datetime
from queue import Queue
from pathlib import Path
from enum import IntEnum

logger = logging.getLogger(__name__)
class SENSOR_ID(IntEnum):
    FUELCELL_POWER = 1
    FUELCELL_VOLTAGE = 2
    FUELCELL_CURRENT = 3
    BATTERY_POWER = 4
    BATTERY_VOLTAGE = 5
    BATTERY_CURRENT = 6
    LOAD_POWER = 7
    LOAD_VOLTAGE = 8
    LOAD_CURRENT = 9
    BATTERY_SOC = 10
    PRESSURE = 11
    THRUST = 12
    THROTTLE = 13

class Database:

    def start():
        Database.queue = Queue()
        Database.running = True

        Database.thread = threading.Thread(target=Database.worker, daemon=True)
        Database.thread.start()

    def stop():
        Database.running = False
        Database.queue.put({
            "action": "stop",
        })
        Database.thread.join()


    def worker():
        Database.start_db()

        Database.current_run = 1

        while Database.running:
            request = Database.queue.get()

            action = request["action"]

            if action == "insert":
                Database._insert(request)

            elif action == "get_latest":
                Database._get_latest(request)

            elif action == "get_csv":
                Database._get_csv(request)

            elif action == "stop":
                Database.stop_db()


    def start_db(filename="data/sensors.db"):
        Database.conn = sqlite3.connect(filename)
        Database.cursor = Database.conn.cursor()

        sql = Database.load_sql("create_run_table")
        Database.cursor.execute(sql)

        sql = Database.load_sql("create_sample_table")
        Database.cursor.execute(sql)

        Database.conn.commit()


    def stop_db():
        Database.conn.close()


    def load_sql(name):
        return Path(f"src/sql/{name}.sql").read_text()


    def insert(sensor_id, value):
        # logger.debug(f"Inserting sensor {sensor_id}")
        Database.queue.put({
            "action": "insert",
            "run_id": Database.current_run,
            "sensor_id": sensor_id,
            "value": value,
        })


    def _insert(request):
        sql = Database.load_sql("insert_sample")

        Database.cursor.execute(sql, (
            request["run_id"],
            datetime.now().isoformat(),
            request["sensor_id"],
            request["value"]
        ))
        Database.conn.commit()


    def get_latest(sensor_id):
        logger.debug(f"Getting latest sensor {sensor_id}")
        response_queue = Queue()

        Database.queue.put({
            "action": "get_latest",
            "sensor_id": sensor_id,
            "response_queue": response_queue
        })

        return response_queue.get()  # blocks until result arrives


    def _get_latest(request):
        sql = Database.load_sql("get_latest")

        Database.cursor.execute(sql, (request["sensor_id"],))
        result = Database.cursor.fetchone()

        if request.get("response_queue"):
            request["response_queue"].put(result[4])


    def get_csv():
        logger.debug(f"Requesting csv ({Database.current_run})")
        Database.queue.put({
            "action": "get_csv",
            "run_id": Database.current_run,
        })

    def _get_csv(request):
        logger.debug(f"Getting csv ({request["run_id"]})")
        sql = Database.load_sql("get_run_samples")

        df = pd.read_sql_query(sql, Database.conn, params=(request["run_id"],))
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        pivot_df = df.pivot(index="timestamp", columns="sensor_id", values="value")
        pivot_df = pivot_df.rename(columns={sensor.value: sensor.name for sensor in SENSOR_ID})

        pivot_df.to_csv("data/run.csv", index=True)


