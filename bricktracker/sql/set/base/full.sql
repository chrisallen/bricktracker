{% extends 'set/base/base.sql' %}

{% block id %}
"bricktracker_sets"."id",
{% endblock %}

{% block total_missing %}
IFNULL("missing_join"."total", 0) AS "total_missing",
{% endblock %}

{% block total_quantity %}
IFNULL("minifigures_join"."total", 0) AS "total_minifigures"
{% endblock %}

{% block join %}
{% if statuses %}
LEFT JOIN "bricktracker_set_statuses"
ON "bricktracker_sets"."id" IS NOT DISTINCT FROM "bricktracker_set_statuses"."bricktracker_set_id"
{% endif %}

-- LEFT JOIN + SELECT to avoid messing the total
LEFT JOIN (
    SELECT
        "missing"."u_id",
        SUM("missing"."quantity") AS "total"
    FROM "missing"
    {% block where_missing %}{% endblock %}
    GROUP BY "u_id"
) "missing_join"
ON "bricktracker_sets"."id" IS NOT DISTINCT FROM "missing_join"."u_id"

-- LEFT JOIN + SELECT to avoid messing the total
LEFT JOIN (
    SELECT
       "minifigures"."u_id",
       SUM("minifigures"."quantity") AS "total"
    FROM "minifigures"
    {% block where_minifigures %}{% endblock %}
    GROUP BY "u_id"
) "minifigures_join"
ON "bricktracker_sets"."id" IS NOT DISTINCT FROM "minifigures_join"."u_id"
{% endblock %}