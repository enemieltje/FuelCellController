CREATE TABLE IF NOT EXISTS test_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    started_at DATETIME,
    ended_at DATETIME,
    notes TEXT
);
