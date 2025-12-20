DELETE FROM bricktracker_set_statuses
WHERE id IN (
    SELECT bs.id
    FROM bricktracker_sets bs
    WHERE NOT EXISTS (
        SELECT 1 FROM rebrickable_sets rs WHERE rs."set" = bs."set"
    )
);