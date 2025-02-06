UPDATE "bricktracker_metadata_purchase_locations"
SET "{{field}}" = :value
WHERE "bricktracker_metadata_purchase_locations"."id" IS NOT DISTINCT FROM :id
