import sqlite3
import logging
import pandas as pd
import threading
from datetime import datetime
from queue import Queue
from pathlib import Path

logger = logging.getLogger(__name__)

class Database:
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

    def start():
        Database.queue = Queue()
        Database.running = True

        Database.thread = threading.Thread(target=Database.worker, daemon=True)
        Database.thread.start()

    def stop():
        Database.thread.join()

    def worker():
        Database.start_db()

        while Database.running:
            request = Database.queue.get()

            action = request["action"]

            # -------------------------
            # INSERT
            # -------------------------
            if action == "insert":
                sql = Database.load_sql("insert_sample")

                Database.cursor.execute(sql, (
                    request["run_id"],
                    datetime.now().isoformat(),
                    request["sensor_id"],
                    request["value"]
                ))
                Database.conn.commit()

            # -------------------------
            # GET LATEST
            # -------------------------
            elif action == "get_latest":
                sql = Database.load_sql("get_latest")

                Database.cursor.execute(sql, (request["sensor_id"],))
                result = Database.cursor.fetchone()

                if request.get("response_queue"):
                    request["response_queue"].put(result)


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

    def insert(sensor_id, value, run_id=0):
        Database.queue.put({
            "action": "insert",
            "run_id": run_id,
            "sensor_id": sensor_id,
            "value": value,
        })

    def get_latest(sensor_id):
        response_queue = Queue()

        Database.queue.put({
            "action": "get_latest",
            "sensor_id": sensor_id,
            "response_queue": response_queue
        })

        return response_queue.get()  # blocks until result arrives

    # def insert(sensor_id, value, run_id=0):
    #     sql = Database.load_sql("insert_sample")

    #     Database.cursor.execute(
    #         sql, (
    #             run_id,
    #             datetime.now().isoformat(),
    #             sensor_id,
    #             value
    #             )
    #         )
    #     Database.conn.commit()

    # def get_run(run_id=0):
    #     sql = Database.load_sql("get_run_samples")
    #     Database.cursor.execute(sql, (run_id,))
    #     rows = Database.cursor.fetchall()

    #     for row in rows:
    #         logger.debug(row)

    #     return rows

    # def get_csv(run_id=0):
    #     sql = Database.load_sql("get_run_samples")
    #     df = pd.read_sql_query(sql, Database.conn, params=(run_id,))
    #     df.pivot(index="timestamp", columns="sensor_id", values="value")
    #     df.to_csv("data/run.csv", index=False)

    # def get_latest(sensor_id):
    #     sql = Database.load_sql("get_latest")
    #     Database.cursor.execute(sql, sensor_id)
    #     sample = Database.cursor.fetchOne()
    #     logger.debug(sample)
    #     return sample

