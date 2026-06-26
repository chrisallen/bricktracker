UPDATE "bricktracker_metadata_custom_fields"
SET "{{field}}" = :value
WHERE "bricktracker_metadata_custom_fields"."id" IS NOT DISTINCT FROM :id
