UPDATE test_runs
SET ended_at = COALESCE(ended_at, ?)
WHERE id = ?;
