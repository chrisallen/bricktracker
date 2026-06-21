-- Distinct set numbers in the collection. Used to intersect with the
-- filesystem instructions list (which is not in the database) for the
-- instructions statistics (#154).
SELECT DISTINCT "bricktracker_sets"."set" AS "set"
FROM "bricktracker_sets"
