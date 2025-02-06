UPDATE "bricktracker_sets"
SET "purchase_location" = :value
WHERE "bricktracker_sets"."id" IS NOT DISTINCT FROM :set_id
