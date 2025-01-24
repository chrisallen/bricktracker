{% extends 'minifigure/base/select.sql' %}

{% block total_missing %}
SUM(IFNULL("missing"."quantity", 0)) AS "total_missing",
{% endblock %}

{% block join %}
LEFT JOIN "missing"
ON "minifigures"."fig_num" IS NOT DISTINCT FROM "missing"."set_num"
AND "minifigures"."u_id" IS NOT DISTINCT FROM "missing"."u_id"
{% endblock %}

{% block where %}
WHERE "minifigures"."fig_num" IN (
    SELECT
        "missing"."set_num"
    FROM "missing"

    WHERE "missing"."color_id" IS NOT DISTINCT FROM :color_id
    AND "missing"."element_id" IS NOT DISTINCT FROM :element_id
    AND "missing"."part_num" IS NOT DISTINCT FROM :part_num

    GROUP BY "missing"."set_num"
)
{% endblock %}

{% block group %}
GROUP BY
    "minifigures"."fig_num"
{% endblock %}
