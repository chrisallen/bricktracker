BEGIN TRANSACTION;

ALTER TABLE "bricktracker_set_statuses"
DROP COLUMN "status_{{ id }}";

DELETE FROM "bricktracker_set_checkboxes"
WHERE "bricktracker_set_checkboxes"."id" IS NOT DISTINCT FROM '{{ id }}';

COMMIT;