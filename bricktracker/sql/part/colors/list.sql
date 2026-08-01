{# Colours that actually occur among the parts, so the dropdown never offers one that
   cannot match. All three part sources are covered: a colour that only exists on an
   individual part or on an individual minifigure part used to be unselectable.

   problem_only narrows it to parts with something missing or damaged. #}
SELECT DISTINCT
    "color_id",
    "color_name",
    "color_rgb"
FROM (
    -- Set parts
    SELECT DISTINCT
        "rebrickable_parts"."color_id" AS "color_id",
        "rebrickable_parts"."color_name" AS "color_name",
        "rebrickable_parts"."color_rgb" AS "color_rgb"
    FROM "rebrickable_parts"
    INNER JOIN "bricktracker_parts"
    ON "bricktracker_parts"."part" IS NOT DISTINCT FROM "rebrickable_parts"."part"
    AND "bricktracker_parts"."color" IS NOT DISTINCT FROM "rebrickable_parts"."color_id"
    {% if owner_id %}
    INNER JOIN "bricktracker_set_owners"
    ON "bricktracker_parts"."id" IS NOT DISTINCT FROM "bricktracker_set_owners"."id"
    {% endif %}
    {% set set_conditions = [] %}
    {% if problem_only %}
      {% set _ = set_conditions.append('("bricktracker_parts"."missing" > 0 OR "bricktracker_parts"."damaged" > 0)') %}
    {% endif %}
    {% if owner_id %}
      {% set _ = set_conditions.append('"bricktracker_set_owners"."owner_' ~ owner_id ~ '" = 1') %}
    {% endif %}
    {% if set_conditions %}
    WHERE {{ set_conditions | join(' AND ') }}
    {% endif %}

    UNION

    -- Individual parts
    SELECT DISTINCT
        "rebrickable_parts"."color_id" AS "color_id",
        "rebrickable_parts"."color_name" AS "color_name",
        "rebrickable_parts"."color_rgb" AS "color_rgb"
    FROM "rebrickable_parts"
    INNER JOIN "bricktracker_individual_parts"
    ON "bricktracker_individual_parts"."part" IS NOT DISTINCT FROM "rebrickable_parts"."part"
    AND "bricktracker_individual_parts"."color" IS NOT DISTINCT FROM "rebrickable_parts"."color_id"
    {% if owner_id %}
    INNER JOIN "bricktracker_set_owners"
    ON "bricktracker_individual_parts"."id" IS NOT DISTINCT FROM "bricktracker_set_owners"."id"
    {% endif %}
    {% set individual_conditions = [] %}
    {% if problem_only %}
      {% set _ = individual_conditions.append('("bricktracker_individual_parts"."missing" > 0 OR "bricktracker_individual_parts"."damaged" > 0)') %}
    {% endif %}
    {% if owner_id %}
      {% set _ = individual_conditions.append('"bricktracker_set_owners"."owner_' ~ owner_id ~ '" = 1') %}
    {% endif %}
    {% if individual_conditions %}
    WHERE {{ individual_conditions | join(' AND ') }}
    {% endif %}

    UNION

    -- Individual minifigure parts
    SELECT DISTINCT
        "rebrickable_parts"."color_id" AS "color_id",
        "rebrickable_parts"."color_name" AS "color_name",
        "rebrickable_parts"."color_rgb" AS "color_rgb"
    FROM "rebrickable_parts"
    INNER JOIN "bricktracker_individual_minifigure_parts"
    ON "bricktracker_individual_minifigure_parts"."part" IS NOT DISTINCT FROM "rebrickable_parts"."part"
    AND "bricktracker_individual_minifigure_parts"."color" IS NOT DISTINCT FROM "rebrickable_parts"."color_id"
    {% if owner_id %}
    INNER JOIN "bricktracker_set_owners"
    ON "bricktracker_individual_minifigure_parts"."id" IS NOT DISTINCT FROM "bricktracker_set_owners"."id"
    {% endif %}
    {% set minifigure_conditions = [] %}
    {% if problem_only %}
      {% set _ = minifigure_conditions.append('("bricktracker_individual_minifigure_parts"."missing" > 0 OR "bricktracker_individual_minifigure_parts"."damaged" > 0)') %}
    {% endif %}
    {% if owner_id %}
      {% set _ = minifigure_conditions.append('"bricktracker_set_owners"."owner_' ~ owner_id ~ '" = 1') %}
    {% endif %}
    {% if minifigure_conditions %}
    WHERE {{ minifigure_conditions | join(' AND ') }}
    {% endif %}
)
ORDER BY "color_name" ASC
