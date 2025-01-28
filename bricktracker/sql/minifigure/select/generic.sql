{% extends 'minifigure/base/base.sql' %}

{% block total_missing %}
IFNULL("missing_join"."total", 0) AS "total_missing",
{% endblock %}

{% block total_quantity %}
SUM(IFNULL("bricktracker_minifigures"."quantity", 0)) AS "total_quantity",
{% endblock %}

{% block total_sets %}
COUNT(DISTINCT "bricktracker_minifigures"."id") AS "total_sets"
{% endblock %}

{% block join %}
-- LEFT JOIN + SELECT to avoid messing the total
LEFT JOIN (
    SELECT
        "bricktracker_parts"."figure",
        SUM("bricktracker_parts"."missing") AS "total"
    FROM "bricktracker_parts"
    WHERE "bricktracker_parts"."figure" IS NOT DISTINCT FROM :figure
    GROUP BY "bricktracker_parts"."figure"
) "missing_join"
ON "rebrickable_minifigures"."figure" IS NOT DISTINCT FROM "missing_join"."figure"
{% endblock %}

{% block where %}
WHERE "rebrickable_minifigures"."figure" IS NOT DISTINCT FROM :figure
{% endblock %}

{% block group %}
GROUP BY
    "rebrickable_minifigures"."figure"
{% endblock %}
