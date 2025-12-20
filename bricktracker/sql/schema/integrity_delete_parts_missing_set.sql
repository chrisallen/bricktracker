-- Delete parts that reference non-existent sets

DELETE FROM bricktracker_parts
WHERE rowid IN (
    SELECT bp.rowid
    FROM bricktracker_parts bp
    WHERE NOT EXISTS (
        SELECT 1 FROM bricktracker_sets bs WHERE bs.id = bp.id
    )
);
