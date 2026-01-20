-- Delete orphaned parts (bricktracker_parts records without parent rebrickable_parts)

DELETE FROM bricktracker_parts
WHERE (id, figure, part, color, spare) IN (
    SELECT bp.id, bp.figure, bp.part, bp.color, bp.spare
    FROM bricktracker_parts bp
    WHERE NOT EXISTS (
        SELECT 1 FROM rebrickable_parts rp WHERE rp.part = bp.part AND rp.color_id = bp.color
    )
);
