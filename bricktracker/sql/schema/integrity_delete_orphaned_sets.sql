-- Delete orphaned sets (bricktracker_sets records without parent rebrickable_sets)

DELETE FROM bricktracker_sets
WHERE "set" IN (
    SELECT bs."set"
    FROM bricktracker_sets bs
    WHERE NOT EXISTS (
        SELECT 1 FROM rebrickable_sets rs WHERE rs."set" = bs."set"
    )
);
