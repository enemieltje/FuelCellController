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
        logger.info("Starting Database")
        Database.queue = Queue()
        Database.running = True
        Database.current_run = None

        Database.thread = threading.Thread(target=Database.worker, daemon=True)
        Database.thread.start()

    def stop():
        Database.stop_run()
        Database.running = False
        Database.queue.put({
            "action": "stop",
        })
        Database.thread.join()

    def worker():
        Database.start_db()
        # Database.current_run = Database.create_run()
        # logger.debug(f"Started Run:\n{Database.current_run}")

        while Database.running:
            request = Database.queue.get()

            action = request["action"]

            if action == "insert":
                Database._insert(request)

            elif action == "get_latest":
                Database._get_latest(request)

            elif action == "get_csv":
                Database._get_csv(request)

            elif action == "get_current_run":
                Database._get_current_run(request)

            elif action == "get_runs":
                Database._get_runs(request)

            elif action == "get_run_name":
                Database._get_run_name(request)

            elif action == "start_run":
                Database._start_run(request)

            elif action == "update_run":
                Database._update_run(request)

            elif action == "stop_run":
                Database._stop_run(request)

            elif action == "export_run_csv":
                Database._export_run_csv(request)

            elif action == "stop":
                Database.stop_db()

    def start_db(filename="data/sensors.db"):
        logger.debug("Connecting to Database...")
        Database.conn = sqlite3.connect(filename)
        Database.cursor = Database.conn.cursor()

        sql = Database.load_sql("create_run_table")
        Database.cursor.execute(sql)

        sql = Database.load_sql("create_sample_table")
        Database.cursor.execute(sql)

        Database.conn.commit()
        logger.debug("Database Connected!")

    def stop_db():
        Database.conn.close()

    def create_run():
        sql = Database.load_sql("insert_run")
        started_at = datetime.now().isoformat()

        Database.cursor.execute(sql, (
            f"Run {started_at}",
            started_at,
        ))
        Database.conn.commit()

        return Database.cursor.lastrowid

    def row_to_dict(row):
        if row is None:
            return None

        return {
            description[0]: value
            for description, value in zip(Database.cursor.description, row)
        }

    def request(action, **kwargs):
        response_queue = Queue()
        kwargs["action"] = action
        kwargs["response_queue"] = response_queue
        Database.queue.put(kwargs)
        return response_queue.get()

    def load_sql(name):
        return Path(f"src/sql/{name}.sql").read_text()

    def get_all_sensors():
        logger.debug("Getting All Sensors")
        sensor_data = {sensor.name: Database.get_latest(
            sensor.value) for sensor in SENSOR_ID}
        logger.debug(sensor_data)
        return sensor_data

    def insert(sensor_id, value):
        if Database.current_run is None:
            return

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
        if result is None:
            result = (0, 0, "", 0, 0)
        logger.debug(result)

        if request.get("response_queue"):
            request["response_queue"].put(result[4])

    def get_current_run():
        return Database.request("get_current_run")

    def _get_current_run(request):
        run = None

        if Database.current_run is not None:
            Database.cursor.execute(
                "SELECT * FROM test_runs WHERE id = ?",
                (Database.current_run,)
            )
            run = Database.row_to_dict(Database.cursor.fetchone())

        request["response_queue"].put(run)

    def get_runs():
        # logger.debug("Getting Runs")
        return Database.request("get_runs")

    def _get_runs(request):
        sql = Database.load_sql("get_runs")

        Database.cursor.execute(sql)
        rows = Database.cursor.fetchall()
        columns = [description[0]
                   for description in Database.cursor.description]
        runs = [
            {column: value for column, value in zip(columns, row)}
            for row in rows
        ]

        request["response_queue"].put(runs)

    def start_run(name=None, notes=None):
        return Database.request("start_run", name=name, notes=notes)

    def _start_run(request):
        if Database.current_run is not None:
            Database._stop_run({
                "run_id": Database.current_run,
                "response_queue": None,
            })

        Database.current_run = Database.create_run()
        logger.info(f"Started New Run: {Database.current_run}")

        if request.get("name") is not None or request.get("notes") is not None:
            Database._update_run({
                "run_id": Database.current_run,
                "name": request.get("name"),
                "notes": request.get("notes"),
                "response_queue": None,
            })

        Database._get_current_run(request)

    def update_run(run_id, name=None, notes=None):
        return Database.request("update_run", run_id=run_id, name=name, notes=notes)

    def _update_run(request):
        sql = Database.load_sql("update_run")

        Database.cursor.execute(sql, (
            request.get("name"),
            request.get("notes"),
            request["run_id"],
        ))
        Database.conn.commit()

        if request.get("response_queue"):
            Database.cursor.execute(
                "SELECT * FROM test_runs WHERE id = ?",
                (request["run_id"],)
            )
            request["response_queue"].put(
                Database.row_to_dict(Database.cursor.fetchone()))

    def stop_run(run_id=None):
        return Database.request("stop_run", run_id=run_id)

    def _stop_run(request):
        run_id = request.get("run_id") or Database.current_run

        if run_id is None:
            if request.get("response_queue"):
                request["response_queue"].put(None)
            return

        logger.info(f"Stopped Run: {run_id}")
        sql = Database.load_sql("stop_run")
        Database.cursor.execute(sql, (
            datetime.now().isoformat(),
            run_id,
        ))
        Database.conn.commit()

        if run_id == Database.current_run:
            Database.current_run = None

        if request.get("response_queue"):
            Database.cursor.execute(
                "SELECT * FROM test_runs WHERE id = ?",
                (run_id,)
            )
            request["response_queue"].put(
                Database.row_to_dict(Database.cursor.fetchone()))

    def export_run_csv(run_id):
        return Database.request("export_run_csv", run_id=run_id)

    def _export_run_csv(request):
        csv_text = Database._get_csv(request)
        request["response_queue"].put(csv_text)

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
        pivot_df = df.pivot(index="timestamp",
                            columns="sensor_id", values="value")
        pivot_df = pivot_df.rename(
            columns={sensor.value: sensor.name for sensor in SENSOR_ID})

        return pivot_df.to_csv(index=True)

    def get_run_name(run_id=None):
        return Database.request("get_run_name", run_id=run_id)

    def _get_run_name(request):
        logger.debug(f"Getting run name ({request["run_id"]})")
        run_id = request.get("run_id") or Database.current_run
        sql = Database.load_sql("get_run_name")

        Database.cursor.execute(sql, (
            run_id,
        ))
        result = Database.cursor.fetchone()
        if result is None:
            result = (0, 0)

        request["response_queue"].put(result[1])
