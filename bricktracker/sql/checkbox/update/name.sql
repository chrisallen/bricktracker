UPDATE "bricktracker_set_checkboxes"
SET "name" = :safe_name
WHERE "bricktracker_set_checkboxes"."id" IS NOT DISTINCT FROM :id
