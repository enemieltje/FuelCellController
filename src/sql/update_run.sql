UPDATE test_runs
SET
    name = COALESCE(?, name),
    notes = COALESCE(?, notes)
WHERE id = ?;
