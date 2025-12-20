-- Database integrity check summary
-- Returns count of each type of integrity issue

SELECT 'orphaned_sets' as issue_type, COUNT(*) as count,
       'Sets in bricktracker_sets without matching rebrickable_sets record' as description
FROM bricktracker_sets bs
WHERE NOT EXISTS (
    SELECT 1 FROM rebrickable_sets rs WHERE rs."set" = bs."set"
)
UNION ALL
SELECT 'orphaned_parts' as issue_type, COUNT(*) as count,
       'Parts in bricktracker_parts without matching rebrickable_parts record' as description
FROM bricktracker_parts bp
WHERE NOT EXISTS (
    SELECT 1 FROM rebrickable_parts rp WHERE rp.part = bp.part AND rp.color_id = bp.color
)
UNION ALL
SELECT 'parts_missing_set' as issue_type, COUNT(DISTINCT bp.id) as count,
       'Parts referencing non-existent sets in bricktracker_sets' as description
FROM bricktracker_parts bp
WHERE NOT EXISTS (
    SELECT 1 FROM bricktracker_sets bs WHERE bs.id = bp.id
)
ORDER BY count DESC;
