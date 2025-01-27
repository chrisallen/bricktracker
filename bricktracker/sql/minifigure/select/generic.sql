{% extends 'minifigure/base/base.sql' %}

{% block total_missing %}
SUM(IFNULL("missing"."quantity", 0)) AS "total_missing",
{% endblock %}

{% block total_quantity %}
SUM(IFNULL("bricktracker_minifigures"."quantity", 0)) AS "total_quantity",
{% endblock %}

{% block total_sets %}
COUNT(DISTINCT "bricktracker_minifigures"."id") AS "total_sets"
{% endblock %}

{% block join %}
LEFT JOIN "missing"
ON "rebrickable_minifigures"."figure" IS NOT DISTINCT FROM "missing"."set_num"
AND "bricktracker_minifigures"."id" IS NOT DISTINCT FROM "missing"."u_id"
{% endblock %}

{% block where %}
WHERE "rebrickable_minifigures"."figure" IS NOT DISTINCT FROM :figure
{% endblock %}

{% block group %}
GROUP BY
    "rebrickable_minifigures"."figure"
{% endblock %}
