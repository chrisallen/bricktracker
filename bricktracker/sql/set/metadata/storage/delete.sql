BEGIN TRANSACTION;

DELETE FROM "bricktracker_metadata_storages"
WHERE "bricktracker_metadata_storages"."id" IS NOT DISTINCT FROM '{{ id }}';

UPDATE "bricktracker_sets"
SET "storage" = NULL
WHERE "bricktracker_sets"."storage" IS NOT DISTINCT FROM '{{ id }}';

COMMIT;