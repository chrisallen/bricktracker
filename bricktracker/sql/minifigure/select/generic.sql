{% extends 'minifigure/base/base.sql' %}

{% block total_missing %}
IFNULL("problem_join"."total_missing", 0) AS "total_missing",
{% endblock %}

{% block total_damaged %}
IFNULL("problem_join"."total_damaged", 0) AS "total_damaged",
{% endblock %}

{% block total_quantity %}
SUM(IFNULL("bricktracker_minifigures"."quantity", 0)) AS "total_quantity",
{% endblock %}

{% block total_sets %}
IFNULL(COUNT(DISTINCT "bricktracker_minifigures"."id"), 0) AS "total_sets"
{% endblock %}

{% block join %}
-- LEFT JOIN + SELECT to avoid messing the total
LEFT JOIN (
    SELECT
        "bricktracker_parts"."figure",
        SUM("bricktracker_parts"."missing") AS "total_missing",
        SUM("bricktracker_parts"."damaged") AS "total_damaged"
    FROM "bricktracker_parts"
    WHERE "bricktracker_parts"."figure" IS NOT DISTINCT FROM :figure
    GROUP BY "bricktracker_parts"."figure"
) "problem_join"
ON "rebrickable_minifigures"."figure" IS NOT DISTINCT FROM "problem_join"."figure"
{% endblock %}

{% block where %}
WHERE "rebrickable_minifigures"."figure" IS NOT DISTINCT FROM :figure
{% endblock %}

{% block group %}
GROUP BY
    "rebrickable_minifigures"."figure"
{% endblock %}
