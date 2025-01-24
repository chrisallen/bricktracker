{% extends 'part/base/select.sql' %}

{% block total_missing %}
SUM(IFNULL("missing"."quantity", 0)) AS "total_missing",
{% endblock %}

{% block total_sets %}
COUNT("inventory"."u_id")  - COUNT("minifigures"."u_id") AS "total_sets",
{% endblock %}

{% block total_minifigures %}
SUM(IFNULL("minifigures"."quantity", 0)) AS "total_minifigures"
{% endblock %}

{% block join %}
INNER JOIN "missing"
ON "missing"."set_num" IS NOT DISTINCT FROM "inventory"."set_num"
AND "missing"."id" IS NOT DISTINCT FROM "inventory"."id"
AND "missing"."part_num" IS NOT DISTINCT FROM "inventory"."part_num"
AND "missing"."color_id" IS NOT DISTINCT FROM "inventory"."color_id"
AND "missing"."element_id" IS NOT DISTINCT FROM "inventory"."element_id"
AND "missing"."u_id" IS NOT DISTINCT FROM "inventory"."u_id"

LEFT JOIN "minifigures"
ON "missing"."set_num" IS NOT DISTINCT FROM "minifigures"."fig_num"
AND "missing"."u_id" IS NOT DISTINCT FROM "minifigures"."u_id"
{% endblock %}

{% block group %}
GROUP BY
    "inventory"."part_num",
    "inventory"."name",
    "inventory"."color_id",
    "inventory"."is_spare",
    "inventory"."element_id"
{% endblock %}
