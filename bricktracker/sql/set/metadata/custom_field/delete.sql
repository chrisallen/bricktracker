BEGIN TRANSACTION;

ALTER TABLE "bricktracker_set_custom_fields"
DROP COLUMN "custom_field_{{ id }}";

DELETE FROM "bricktracker_metadata_custom_fields"
WHERE "bricktracker_metadata_custom_fields"."id" IS NOT DISTINCT FROM '{{ id }}';

COMMIT;
