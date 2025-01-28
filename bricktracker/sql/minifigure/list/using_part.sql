{% extends 'minifigure/base/base.sql' %}

{% block total_quantity %}
SUM("bricktracker_minifigures"."quantity") AS "total_quantity",
{% endblock %}

{% block where %}
WHERE "rebrickable_minifigures"."figure" IN (
    SELECT "bricktracker_parts"."figure"
    FROM "bricktracker_parts"
    WHERE "bricktracker_parts"."part" IS NOT DISTINCT FROM :part
    AND "bricktracker_parts"."color" IS NOT DISTINCT FROM :color
    AND "bricktracker_parts"."figure" IS NOT NULL
    GROUP BY "bricktracker_parts"."figure"
)
{% endblock %}

{% block group %}
GROUP BY
    "rebrickable_minifigures"."figure"
{% endblock %}
