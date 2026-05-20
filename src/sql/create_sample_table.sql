CREATE TABLE IF NOT EXISTS sensor_samples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER,
    timestamp DATETIME,
    fuelcell_power REAL,
    fuelcell_voltage REAL,
    fuelcell_current REAL,
    battery_power REAL,
    battery_voltage REAL,
    battery_current REAL,
    load_power REAL,
    load_voltage REAL,
    load_current REAL,
    battery_soc REAL,
    pressure REAL,
    thrust REAL,
    FOREIGN KEY(run_id) REFERENCES test_runs(id)
);
