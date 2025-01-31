{% extends 'minifigure/base/base.sql' %}

{% block total_damaged %}
SUM("bricktracker_parts"."damaged") AS "total_damaged",
{% endblock %}

{% block join %}
LEFT JOIN "bricktracker_parts"
ON "bricktracker_minifigures"."id" IS NOT DISTINCT FROM "bricktracker_parts"."id"
AND "rebrickable_minifigures"."figure" IS NOT DISTINCT FROM "bricktracker_parts"."figure"
{% endblock %}

{% block where %}
WHERE "rebrickable_minifigures"."figure" IN (
    SELECT "bricktracker_parts"."figure"
    FROM "bricktracker_parts"
    WHERE "bricktracker_parts"."part" IS NOT DISTINCT FROM :part
    AND "bricktracker_parts"."color" IS NOT DISTINCT FROM :color
    AND "bricktracker_parts"."figure" IS NOT NULL
    AND "bricktracker_parts"."damaged" > 0
    GROUP BY "bricktracker_parts"."figure"
)
{% endblock %}

{% block group %}
GROUP BY
    "rebrickable_minifigures"."figure"
{% endblock %}
