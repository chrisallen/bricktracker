UPDATE "bricktracker_set_checkboxes"
SET "{{field}}" = :value
WHERE "bricktracker_set_checkboxes"."id" IS NOT DISTINCT FROM :id
