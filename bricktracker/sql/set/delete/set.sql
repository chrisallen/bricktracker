-- A bit unsafe as it does not use a prepared statement but it
-- should not be possible to inject anything through the {{ id }} context

BEGIN TRANSACTION;

DELETE FROM "bricktracker_sets"
WHERE "bricktracker_sets"."id" IS NOT DISTINCT FROM '{{ id }}';

DELETE FROM "bricktracker_set_owners"
WHERE "bricktracker_set_owners"."id" IS NOT DISTINCT FROM '{{ id }}';

DELETE FROM "bricktracker_set_statuses"
WHERE "bricktracker_set_statuses"."id" IS NOT DISTINCT FROM '{{ id }}';

DELETE FROM "bricktracker_set_tags"
WHERE "bricktracker_set_tags"."id" IS NOT DISTINCT FROM '{{ id }}';

DELETE FROM "bricktracker_minifigures"
WHERE "bricktracker_minifigures"."id" IS NOT DISTINCT FROM '{{ id }}';

DELETE FROM "bricktracker_parts"
WHERE "bricktracker_parts"."id" IS NOT DISTINCT FROM '{{ id }}';

COMMIT;