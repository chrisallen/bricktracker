SELECT COUNT(*) as "total_count"
FROM (
    SELECT DISTINCT
        "bricktracker_parts"."part",
        "bricktracker_parts"."color",
        "bricktracker_parts"."spare"
    FROM "bricktracker_parts"

    INNER JOIN "rebrickable_parts"
    ON "bricktracker_parts"."part" IS NOT DISTINCT FROM "rebrickable_parts"."part"
    AND "bricktracker_parts"."color" IS NOT DISTINCT FROM "rebrickable_parts"."color_id"

    LEFT JOIN "bricktracker_minifigures"
    ON "bricktracker_parts"."id" IS NOT DISTINCT FROM "bricktracker_minifigures"."id"
    AND "bricktracker_parts"."figure" IS NOT DISTINCT FROM "bricktracker_minifigures"."figure"

    {% set conditions = [] %}
    {% if color_id and color_id != 'all' %}
      {% set _ = conditions.append('"bricktracker_parts"."color" = ' ~ color_id) %}
    {% endif %}
    {% if search_query %}
      {% set search_condition = '(LOWER("rebrickable_parts"."name") LIKE LOWER(\'%' ~ search_query ~ '%\') OR LOWER("rebrickable_parts"."color_name") LIKE LOWER(\'%' ~ search_query ~ '%\') OR LOWER("bricktracker_parts"."part") LIKE LOWER(\'%' ~ search_query ~ '%\'))' %}
      {% set _ = conditions.append(search_condition) %}
    {% endif %}
    {% if conditions %}
    WHERE {{ conditions | join(' AND ') }}
    {% endif %}
)