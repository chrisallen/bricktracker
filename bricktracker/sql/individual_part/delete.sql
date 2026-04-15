-- A bit unsafe as it does not use a prepared statement but it
-- should not be possible to inject anything through the {{ id }} context

BEGIN TRANSACTION;

-- Delete metadata from consolidated tables
DELETE FROM "bricktracker_set_owners"
WHERE "id" IS NOT DISTINCT FROM '{{ id }}';

DELETE FROM "bricktracker_set_tags"
WHERE "id" IS NOT DISTINCT FROM '{{ id }}';

-- Delete the individual part itself
DELETE FROM "bricktracker_individual_parts"
WHERE "id" IS NOT DISTINCT FROM '{{ id }}';

COMMIT;
