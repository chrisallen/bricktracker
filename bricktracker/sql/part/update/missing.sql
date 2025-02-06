UPDATE "bricktracker_parts"
SET "missing" = :missing
WHERE "bricktracker_parts"."id" IS NOT DISTINCT FROM :id
AND "bricktracker_parts"."figure" IS NOT DISTINCT FROM :figure
AND "bricktracker_parts"."part" IS NOT DISTINCT FROM :part
AND "bricktracker_parts"."color" IS NOT DISTINCT FROM :color
AND "bricktracker_parts"."spare" IS NOT DISTINCT FROM :spare
