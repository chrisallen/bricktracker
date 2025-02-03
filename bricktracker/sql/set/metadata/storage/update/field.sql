UPDATE "bricktracker_metadata_storages"
SET "{{field}}" = :value
WHERE "bricktracker_metadata_storages"."id" IS NOT DISTINCT FROM :id
