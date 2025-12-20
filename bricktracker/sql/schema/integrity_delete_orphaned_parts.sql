-- Delete orphaned parts (bricktracker_parts records without parent rebrickable_parts)

DELETE FROM bricktracker_parts
WHERE rowid IN (
    SELECT bp.rowid
    FROM bricktracker_parts bp
    WHERE NOT EXISTS (
        SELECT 1 FROM rebrickable_parts rp WHERE rp.part = bp.part AND rp.color_id = bp.color
    )
);
