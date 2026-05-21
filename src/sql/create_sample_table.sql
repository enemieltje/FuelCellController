CREATE TABLE IF NOT EXISTS sensor_samples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER,
    timestamp DATETIME,
    sensor_id INTEGER,
    value REAL,
    FOREIGN KEY(run_id) REFERENCES test_runs(id)
);
