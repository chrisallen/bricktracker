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
        "missing"."set_num",
        "missing"."u_id",
        SUM("missing"."quantity") AS total
    FROM "missing"
    GROUP BY
        "missing"."set_num",
        "missing"."u_id"
) missing_join
ON "bricktracker_minifigures"."id" IS NOT DISTINCT FROM "missing_join"."u_id"
AND "rebrickable_minifigures"."figure" IS NOT DISTINCT FROM "missing_join"."set_num"
{% endblock %}

{% block group %}
GROUP BY
    "rebrickable_minifigures"."figure"
{% endblock %}
