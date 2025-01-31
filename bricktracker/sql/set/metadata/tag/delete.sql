BEGIN TRANSACTION;

ALTER TABLE "bricktracker_set_tags"
DROP COLUMN "tag_{{ id }}";

DELETE FROM "bricktracker_metadata_tags"
WHERE "bricktracker_metadata_tags"."id" IS NOT DISTINCT FROM '{{ id }}';

COMMIT;