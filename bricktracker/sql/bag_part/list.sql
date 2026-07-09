SELECT "bag", "part", "color", "spare", "checked", "missing"
FROM "bricktracker_bag_parts"
WHERE "bricktracker_bag_parts"."id" IS NOT DISTINCT FROM :id
