UPDATE "bricktracker_metadata_tags"
SET "{{field}}" = :value
WHERE "bricktracker_metadata_tags"."id" IS NOT DISTINCT FROM :id
