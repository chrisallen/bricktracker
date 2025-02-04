BEGIN TRANSACTION;

DELETE FROM "bricktracker_metadata_purchase_locations"
WHERE "bricktracker_metadata_purchase_locations"."id" IS NOT DISTINCT FROM '{{ id }}';

UPDATE "bricktracker_sets"
SET "purchase_location" = NULL
WHERE "bricktracker_sets"."purchase_location" IS NOT DISTINCT FROM '{{ id }}';

COMMIT;