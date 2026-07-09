INSERT INTO "bricktracker_bag_parts" ("id", "bag", "part", "color", "spare", "checked")
VALUES (:id, :bag, :part, :color, :spare, :checked)
ON CONFLICT("id", "bag", "part", "color", "spare")
DO UPDATE SET "checked" = excluded."checked"
