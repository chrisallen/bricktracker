BEGIN TRANSACTION;

DELETE FROM "bricktracker_metadata_storages"
WHERE "bricktracker_metadata_statuses"."id" IS NOT DISTINCT FROM '{{ id }}';

COMMIT;