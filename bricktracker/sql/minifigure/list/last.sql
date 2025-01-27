{% extends 'minifigure/base/base.sql' %}

{% block total_missing %}
SUM(IFNULL("missing"."quantity", 0)) AS "total_missing",
{% endblock %}

{% block join %}
LEFT JOIN "missing"
ON "rebrickable_minifigures"."figure" IS NOT DISTINCT FROM "missing"."set_num"
AND "bricktracker_minifigures"."bricktracker_set_id" IS NOT DISTINCT FROM "missing"."u_id"
{% endblock %}

{% block group %}
GROUP BY
    "rebrickable_minifigures"."figure",
    "bricktracker_minifigures"."bricktracker_set_id"
{% endblock %}
