SELECT
    test_runs.id,
    test_runs.name,
    test_runs.started_at,
    test_runs.ended_at,
    test_runs.notes,
    COUNT(sensor_samples.id) AS sample_count
FROM test_runs
LEFT JOIN sensor_samples ON sensor_samples.run_id = test_runs.id
GROUP BY test_runs.id
ORDER BY test_runs.id DESC
