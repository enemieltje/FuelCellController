SELECT *
FROM sensor_samples
WHERE sensor_id = ?
ORDER BY timestamp DESC
LIMIT 1;

