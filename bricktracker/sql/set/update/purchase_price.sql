UPDATE "bricktracker_sets"
SET "purchase_price" = :purchase_price
WHERE "bricktracker_sets"."id" IS NOT DISTINCT FROM :id
