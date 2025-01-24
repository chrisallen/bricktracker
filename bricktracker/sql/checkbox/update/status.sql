UPDATE "bricktracker_set_checkboxes"
SET "{{name}}" = :status
WHERE "bricktracker_set_checkboxes"."id" IS NOT DISTINCT FROM :id
