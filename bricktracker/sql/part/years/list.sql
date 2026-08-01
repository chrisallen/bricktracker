{# Years present among the parts. Only set sourced parts have a year, so individual
   parts and individual minifigure parts are out of scope here by definition.
   problem_only narrows it to parts with something missing or damaged. #}
SELECT DISTINCT
    "rebrickable_sets"."year",
    COUNT(DISTINCT "bricktracker_parts"."part") as "part_count"
FROM "bricktracker_parts"
INNER JOIN "bricktracker_sets"
ON "bricktracker_parts"."id" IS NOT DISTINCT FROM "bricktracker_sets"."id"
INNER JOIN "rebrickable_sets"
ON "bricktracker_sets"."set" IS NOT DISTINCT FROM "rebrickable_sets"."set"
{% if owner_id %}
INNER JOIN "bricktracker_set_owners"
ON "bricktracker_sets"."id" IS NOT DISTINCT FROM "bricktracker_set_owners"."id"
{% endif %}
{% set conditions = [] %}
{% if problem_only %}
  {% set _ = conditions.append('("bricktracker_parts"."missing" > 0 OR "bricktracker_parts"."damaged" > 0)') %}
{% endif %}
{% if owner_id %}
  {% set _ = conditions.append('"bricktracker_set_owners"."owner_' ~ owner_id ~ '" = 1') %}
{% endif %}
{% if conditions %}
WHERE {{ conditions | join(' AND ') }}
{% endif %}
GROUP BY "rebrickable_sets"."year"
ORDER BY "rebrickable_sets"."year" DESC
