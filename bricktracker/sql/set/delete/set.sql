-- A bit unsafe as it does not use a prepared statement but it
-- should not be possible to inject anything through the {{ id }} context

BEGIN TRANSACTION;

DELETE FROM "bricktracker_sets"
WHERE "bricktracker_sets"."id" IS NOT DISTINCT FROM '{{ id }}';

DELETE FROM "bricktracker_set_statuses"
WHERE "bricktracker_set_statuses"."bricktracker_set_id" IS NOT DISTINCT FROM '{{ id }}';

DELETE FROM "minifigures"
WHERE "minifigures"."u_id" IS NOT DISTINCT FROM '{{ id }}';

DELETE FROM "missing"
WHERE "missing"."u_id" IS NOT DISTINCT FROM '{{ id }}';

DELETE FROM "inventory"
WHERE "inventory"."u_id" IS NOT DISTINCT FROM '{{ id }}';

COMMIT;