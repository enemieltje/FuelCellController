SELECT *
FROM sensor_samples
WHERE run_id = ?
ORDER BY timestamp
