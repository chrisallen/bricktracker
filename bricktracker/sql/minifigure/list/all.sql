{% extends 'minifigure/base/base.sql' %}

{% block total_missing %}
SUM(IFNULL("missing_join"."total", 0)) AS "total_missing",
{% endblock %}

{% block total_quantity %}
SUM(IFNULL("bricktracker_minifigures"."quantity", 0)) AS "total_quantity",
{% endblock %}

{% block total_sets %}
COUNT("bricktracker_minifigures"."id") AS "total_sets"
{% endblock %}

{% block join %}
-- LEFT JOIN + SELECT to avoid messing the total
LEFT JOIN (
    SELECT
        "bricktracker_parts"."id",
        "bricktracker_parts"."figure",
        SUM("bricktracker_parts"."missing") AS total
    FROM "bricktracker_parts"
    WHERE "bricktracker_parts"."figure" IS NOT NULL
    GROUP BY
        "bricktracker_parts"."id",
        "bricktracker_parts"."figure"
) missing_join
ON "bricktracker_minifigures"."id" IS NOT DISTINCT FROM "missing_join"."id"
AND "rebrickable_minifigures"."figure" IS NOT DISTINCT FROM "missing_join"."figure"
{% endblock %}

{% block group %}
GROUP BY
    "rebrickable_minifigures"."figure"
{% endblock %}
