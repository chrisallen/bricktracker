SELECT DISTINCT
    "rebrickable_parts"."color_id" AS "color_id",
    "rebrickable_parts"."color_name" AS "color_name",
    "rebrickable_parts"."color_rgb" AS "color_rgb"
FROM "rebrickable_parts"
INNER JOIN "bricktracker_parts"
ON "bricktracker_parts"."part" IS NOT DISTINCT FROM "rebrickable_parts"."part"
AND "bricktracker_parts"."color" IS NOT DISTINCT FROM "rebrickable_parts"."color_id"
{% if owner_id and owner_id != 'all' %}
INNER JOIN "bricktracker_sets"
ON "bricktracker_parts"."id" IS NOT DISTINCT FROM "bricktracker_sets"."id"
INNER JOIN "bricktracker_set_owners"
ON "bricktracker_sets"."id" IS NOT DISTINCT FROM "bricktracker_set_owners"."id"
WHERE "bricktracker_set_owners"."owner_{{ owner_id }}" = 1
{% endif %}
ORDER BY "rebrickable_parts"."color_name" ASC