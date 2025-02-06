UPDATE "bricktracker_metadata_owners"
SET "{{field}}" = :value
WHERE "bricktracker_metadata_owners"."id" IS NOT DISTINCT FROM :id
