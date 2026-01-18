-- A bit unsafe as it does not use a prepared statement but it
-- should not be possible to inject anything through the {{ id }} context

BEGIN TRANSACTION;

-- Delete all individual parts associated with this lot
DELETE FROM "bricktracker_individual_parts"
WHERE "lot_id" IS NOT DISTINCT FROM '{{ id }}';

-- Delete lot owners (using consolidated metadata table)
DELETE FROM "bricktracker_set_owners"
WHERE "id" IS NOT DISTINCT FROM '{{ id }}';

-- Delete lot tags (using consolidated metadata table)
DELETE FROM "bricktracker_set_tags"
WHERE "id" IS NOT DISTINCT FROM '{{ id }}';

-- Delete the lot itself
DELETE FROM "bricktracker_individual_part_lots"
WHERE "id" IS NOT DISTINCT FROM '{{ id }}';

COMMIT;
