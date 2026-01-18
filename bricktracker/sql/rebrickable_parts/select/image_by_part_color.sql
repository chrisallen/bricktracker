-- Get image URL for a part/color combination
SELECT "image" FROM "rebrickable_parts"
WHERE "part" = :part AND "color_id" = :color_id
