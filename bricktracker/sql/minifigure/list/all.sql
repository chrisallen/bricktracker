{% extends 'minifigure/base/base.sql' %}

{% block total_missing %}
SUM(IFNULL("problem_join"."total_missing", 0)) AS "total_missing",
{% endblock %}

{% block total_damaged %}
SUM(IFNULL("problem_join"."total_damaged", 0)) AS "total_damaged",
{% endblock %}

{% block total_quantity %}
SUM(IFNULL("bricktracker_minifigures"."quantity", 0)) AS "total_quantity",
{% endblock %}

{% block total_sets %}
IFNULL(COUNT("bricktracker_minifigures"."id"), 0) AS "total_sets"
{% endblock %}

{% block join %}
-- LEFT JOIN + SELECT to avoid messing the total
LEFT JOIN (
    SELECT
        "bricktracker_parts"."id",
        "bricktracker_parts"."figure",
        SUM("bricktracker_parts"."missing") AS "total_missing",
        SUM("bricktracker_parts"."damaged") AS "total_damaged"
    FROM "bricktracker_parts"
    WHERE "bricktracker_parts"."figure" IS NOT NULL
    GROUP BY
        "bricktracker_parts"."id",
        "bricktracker_parts"."figure"
) "problem_join"
ON "bricktracker_minifigures"."id" IS NOT DISTINCT FROM "problem_join"."id"
AND "rebrickable_minifigures"."figure" IS NOT DISTINCT FROM "problem_join"."figure"
{% endblock %}

{% block group %}
GROUP BY
    "rebrickable_minifigures"."figure"
{% endblock %}
