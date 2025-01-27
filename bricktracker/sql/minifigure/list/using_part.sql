{% extends 'minifigure/base/base.sql' %}

{% block total_quantity %}
SUM("bricktracker_minifigures"."quantity") AS "total_quantity",
{% endblock %}

{% block where %}
WHERE "rebrickable_minifigures"."figure" IN (
    SELECT
        "inventory"."set_num"
    FROM "inventory"

    WHERE "inventory"."color_id" IS NOT DISTINCT FROM :color_id
    AND "inventory"."element_id" IS NOT DISTINCT FROM :element_id
    AND "inventory"."part_num" IS NOT DISTINCT FROM :part_num

    GROUP BY "inventory"."set_num"
)
{% endblock %}

{% block group %}
GROUP BY
    "rebrickable_minifigures"."figure"
{% endblock %}
