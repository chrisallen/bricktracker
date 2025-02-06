BEGIN TRANSACTION;

ALTER TABLE "bricktracker_set_statuses"
DROP COLUMN "status_{{ id }}";

DELETE FROM "bricktracker_metadata_statuses"
WHERE "bricktracker_metadata_statuses"."id" IS NOT DISTINCT FROM '{{ id }}';

COMMIT;