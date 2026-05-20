import sqlite3
import logging
import pandas as pd
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class Database:

    def start(filename="data/sensors.db"):
        Database.conn = sqlite3.connect(filename)
        Database.cursor = Database.conn.cursor()

        sql = Database.load_sql("create_run_table")
        Database.cursor.execute(sql)

        sql = Database.load_sql("create_sample_table")
        Database.cursor.execute(sql)

        Database.conn.commit()

    def stop():
        Database.conn.close()


    def load_sql(name):
        return Path(f"src/sql/{name}.sql").read_text()

    def insert(
        fuelcell_power,
        fuelcell_voltage,
        fuelcell_current,
        battery_power,
        battery_voltage,
        battery_current,
        load_power,
        load_voltage,
        load_current,
        battery_soc,
        pressure,
        thrust,
        run_id=0
        ):
        sql = Database.load_sql("insert_sample")

        Database.cursor.execute(
            sql, (
                run_id,
                datetime.now().isoformat(),
                fuelcell_power,
                fuelcell_voltage,
                fuelcell_current,
                battery_power,
                battery_voltage,
                battery_current,
                load_power,
                load_voltage,
                load_current,
                battery_soc,
                pressure,
                thrust,
                )
            )
        Database.conn.commit()

    def get_run(run_id=0):
        sql = Database.load_sql("get_run_samples")
        Database.cursor.execute(sql, (run_id,))
        rows = Database.cursor.fetchall()

        for row in rows:
            logger.debug(row)

        return rows

    def get_csv(run_id=0):
        sql = Database.load_sql("get_run_samples")
        df = pd.read_sql_query(sql, Database.conn, params=(run_id,))
        df.to_csv("data/run.csv", index=False)

    def get_latest():
        sql = Database.load_sql("get_latest")
        Database.cursor.execute(sql)
        sample = Database.cursor.fetchOne()
        logger.debug(sample)
        return sample

