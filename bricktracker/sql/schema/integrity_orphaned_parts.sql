-- Find orphaned parts (bricktracker_parts records without parent rebrickable_parts)

SELECT
    bp.id,
    bp.part,
    bp.color,
    bp.quantity,
    bp.spare,
    bp.missing,
    bp.damaged,
    bs."set" as set_number
FROM bricktracker_parts bp
LEFT JOIN bricktracker_sets bs ON bs.id = bp.id
WHERE NOT EXISTS (
    SELECT 1 FROM rebrickable_parts rp WHERE rp.part = bp.part AND rp.color_id = bp.color
)
ORDER BY bp.id, bp.part, bp.color;
