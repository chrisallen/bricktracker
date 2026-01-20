-- Delete parts that reference non-existent sets

DELETE FROM bricktracker_parts
WHERE (id, figure, part, color, spare) IN (
    SELECT bp.id, bp.figure, bp.part, bp.color, bp.spare
    FROM bricktracker_parts bp
    WHERE NOT EXISTS (
        SELECT 1 FROM bricktracker_sets bs WHERE bs.id = bp.id
    )
);
