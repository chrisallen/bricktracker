SELECT
    "bricktracker_parts"."id",
    "bricktracker_parts"."figure",
    "bricktracker_parts"."part",
    "bricktracker_parts"."color",
    "bricktracker_parts"."spare",
    "bricktracker_parts"."quantity",
    "bricktracker_parts"."element",
    --"bricktracker_parts"."rebrickable_inventory",
    "bricktracker_parts"."missing",
    "bricktracker_parts"."damaged",
    --"rebrickable_parts"."part",
    --"rebrickable_parts"."color_id",
    "rebrickable_parts"."color_name",
    "rebrickable_parts"."color_rgb",
    "rebrickable_parts"."color_transparent",
    "rebrickable_parts"."name",
    --"rebrickable_parts"."category",
    "rebrickable_parts"."image",
    "rebrickable_parts"."image_id",
    "rebrickable_parts"."url",
    "rebrickable_parts"."print",
    {% block total_missing %}
    NULL AS "total_missing", -- dummy for order: total_missing
    {% endblock %}
    {% block total_damaged %}
    NULL AS "total_damaged", -- dummy for order: total_damaged
    {% endblock %}
    {% block total_quantity %}
    NULL AS "total_quantity", -- dummy for order: total_quantity
    {% endblock %}
    {% block total_spare %}
    NULL AS "total_spare", -- dummy for order: total_spare
    {% endblock %}
    {% block total_sets %}
    NULL AS "total_sets", -- dummy for order: total_sets
    {% endblock %}
    {% block total_minifigures %}
    NULL AS "total_minifigures" -- dummy for order: total_minifigures
    {% endblock %}
FROM "bricktracker_parts"

INNER JOIN "rebrickable_parts"
ON "bricktracker_parts"."part" IS NOT DISTINCT FROM "rebrickable_parts"."part"
AND "bricktracker_parts"."color" IS NOT DISTINCT FROM "rebrickable_parts"."color_id"

{% block join %}{% endblock %}

{% block where %}{% endblock %}

{% block group %}{% endblock %}

{% if order %}
ORDER BY {{ order }}
{% endif %}

{% if limit %}
LIMIT {{ limit }}
{% endif %}
