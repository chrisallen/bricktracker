-- Get distinct years from problem parts' sets
SELECT DISTINCT
    "rebrickable_sets"."year",
    COUNT(DISTINCT "bricktracker_parts"."part") as "part_count"
FROM "bricktracker_parts"
INNER JOIN "bricktracker_sets"
ON "bricktracker_parts"."id" IS NOT DISTINCT FROM "bricktracker_sets"."id"
INNER JOIN "rebrickable_sets"
ON "bricktracker_sets"."set" IS NOT DISTINCT FROM "rebrickable_sets"."set"
{% if owner_id and owner_id != 'all' %}
INNER JOIN "bricktracker_set_owners"
ON "bricktracker_sets"."id" IS NOT DISTINCT FROM "bricktracker_set_owners"."id"
{% endif %}
WHERE ("bricktracker_parts"."missing" > 0 OR "bricktracker_parts"."damaged" > 0)
{% if owner_id and owner_id != 'all' %}
AND "bricktracker_set_owners"."owner_{{ owner_id }}" = 1
{% endif %}
GROUP BY "rebrickable_sets"."year"
ORDER BY "rebrickable_sets"."year" DESC
