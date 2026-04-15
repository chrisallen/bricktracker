UPDATE "bricktracker_sets"
SET "description" = :description
WHERE "bricktracker_sets"."id" IS NOT DISTINCT FROM :id
