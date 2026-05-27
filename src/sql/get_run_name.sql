SELECT
    test_runs.id,
    test_runs.name
FROM test_runs
WHERE id = ?
LIMIT 1;

