-- Update existing part quantities during refresh while preserving tracking data
UPDATE "bricktracker_parts"
SET
    "quantity" = :quantity,
    "element" = :element,
    "rebrickable_inventory" = :rebrickable_inventory
WHERE "id" = :id
AND "figure" IS NOT DISTINCT FROM :figure
AND "part" = :part
AND "color" = :color
AND "spare" = :spare
