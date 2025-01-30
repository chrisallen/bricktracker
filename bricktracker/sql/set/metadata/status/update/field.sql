UPDATE "bricktracker_metadata_statuses"
SET "{{field}}" = :value
WHERE "bricktracker_metadata_statuses"."id" IS NOT DISTINCT FROM :id
