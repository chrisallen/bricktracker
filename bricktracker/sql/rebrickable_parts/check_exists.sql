-- Check if a part/color combination exists in rebrickable_parts
SELECT COUNT(*) FROM "rebrickable_parts"
WHERE "part" = :part AND "color_id" = :color_id
