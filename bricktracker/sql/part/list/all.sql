{% extends 'part/base/select.sql' %}

{% block total_missing %}
SUM(IFNULL("missing"."quantity", 0)) AS "total_missing",
{% endblock %}

{% block total_quantity %}
SUM("inventory"."quantity" * IFNULL("minifigures"."quantity", 1)) AS "total_quantity",
{% endblock %}

{% block total_sets %}
COUNT(DISTINCT "bricktracker_sets"."id") AS "total_sets",
{% endblock %}

{% block total_minifigures %}
SUM(IFNULL("minifigures"."quantity", 0)) AS "total_minifigures"
{% endblock %}

{% block join %}
LEFT JOIN "missing"
ON "inventory"."set_num" IS NOT DISTINCT FROM "missing"."set_num"
AND "inventory"."id" IS NOT DISTINCT FROM "missing"."id"
AND "inventory"."part_num" IS NOT DISTINCT FROM "missing"."part_num"
AND "inventory"."color_id" IS NOT DISTINCT FROM "missing"."color_id"
AND "inventory"."element_id" IS NOT DISTINCT FROM "missing"."element_id"
AND "inventory"."u_id" IS NOT DISTINCT FROM "missing"."u_id"

LEFT JOIN "minifigures"
ON "inventory"."set_num" IS NOT DISTINCT FROM "minifigures"."fig_num"
AND "inventory"."u_id" IS NOT DISTINCT FROM "minifigures"."u_id"

LEFT JOIN "bricktracker_sets"
ON "inventory"."u_id" IS NOT DISTINCT FROM "bricktracker_sets"."id"
{% endblock %}

{% block group %}
GROUP BY
    "inventory"."part_num",
    "inventory"."name",
    "inventory"."color_id",
    "inventory"."is_spare",
    "inventory"."element_id"
{% endblock %}
