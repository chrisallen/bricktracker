-- A bit unsafe as it does not use a prepared statement but it
-- should not be possible to inject anything through the {{ id }} context

BEGIN TRANSACTION;

-- Delete associated parts first
DELETE FROM "bricktracker_individual_minifigure_parts"
WHERE "id" IS NOT DISTINCT FROM '{{ id }}';

-- Delete metadata from consolidated tables
DELETE FROM "bricktracker_set_owners"
WHERE "id" IS NOT DISTINCT FROM '{{ id }}';

DELETE FROM "bricktracker_set_statuses"
WHERE "id" IS NOT DISTINCT FROM '{{ id }}';

DELETE FROM "bricktracker_set_tags"
WHERE "id" IS NOT DISTINCT FROM '{{ id }}';

-- Delete the individual minifigure itself
DELETE FROM "bricktracker_individual_minifigures"
WHERE "id" IS NOT DISTINCT FROM '{{ id }}';

COMMIT;
