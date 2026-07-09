INSERT INTO "bricktracker_bag_parts" ("id", "bag", "part", "color", "spare", "missing")
VALUES (:id, :bag, :part, :color, :spare, :missing)
ON CONFLICT("id", "bag", "part", "color", "spare")
DO UPDATE SET "missing" = excluded."missing"
