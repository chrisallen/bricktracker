UPDATE "bricktracker_sets"
SET "storage" = :state
WHERE "bricktracker_sets"."id" IS NOT DISTINCT FROM :set_id
