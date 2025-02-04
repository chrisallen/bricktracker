-- A bit unsafe as it does not use a prepared statement but it
-- should not be possible to inject anything through the {{ set }} context

BEGIN TRANSACTION;

DELETE FROM "bricktracker_wishes"
WHERE "bricktracker_wishes"."set" IS NOT DISTINCT FROM '{{ set }}';

DELETE FROM "bricktracker_wish_owners"
WHERE "bricktracker_wish_owners"."set" IS NOT DISTINCT FROM '{{ set }}';

COMMIT;