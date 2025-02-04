UPDATE "bricktracker_sets"
SET "purchase_date" = :purchase_date
WHERE "bricktracker_sets"."id" IS NOT DISTINCT FROM :id
