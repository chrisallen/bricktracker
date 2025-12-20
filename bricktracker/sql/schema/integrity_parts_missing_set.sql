-- Find parts referencing non-existent sets

SELECT
    bp.id,
    bp.part,
    bp.color,
    bp.quantity,
    bp.spare,
    bp.missing,
    bp.damaged
FROM bricktracker_parts bp
WHERE NOT EXISTS (
    SELECT 1 FROM bricktracker_sets bs WHERE bs.id = bp.id
)
ORDER BY bp.id, bp.part, bp.color;
