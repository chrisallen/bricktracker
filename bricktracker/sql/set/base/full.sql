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
ON "bricktracker_sets"."id" IS NOT DISTINCT FROM "bricktracker_set_statuses"."id"
{% endif %}

-- LEFT JOIN + SELECT to avoid messing the total
LEFT JOIN (
    SELECT
        "bricktracker_parts"."id",
        SUM("bricktracker_parts"."missing") AS "total"
    FROM "bricktracker_parts"
    {% block where_missing %}{% endblock %}
    GROUP BY "bricktracker_parts"."id"
) "missing_join"
ON "bricktracker_sets"."id" IS NOT DISTINCT FROM "missing_join"."id"

-- LEFT JOIN + SELECT to avoid messing the total
LEFT JOIN (
    SELECT
       "bricktracker_minifigures"."id",
       SUM("bricktracker_minifigures"."quantity") AS "total"
    FROM "bricktracker_minifigures"
    {% block where_minifigures %}{% endblock %}
    GROUP BY "bricktracker_minifigures"."id"
) "minifigures_join"
ON "bricktracker_sets"."id" IS NOT DISTINCT FROM "minifigures_join"."id"
{% endblock %}