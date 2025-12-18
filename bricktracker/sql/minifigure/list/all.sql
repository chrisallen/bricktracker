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
{% if theme_id or year %}
-- Join with sets for theme/year filtering
INNER JOIN "bricktracker_sets" AS "filter_sets"
ON "bricktracker_minifigures"."id" IS NOT DISTINCT FROM "filter_sets"."id"
INNER JOIN "rebrickable_sets" AS "filter_rs"
ON "filter_sets"."set" IS NOT DISTINCT FROM "filter_rs"."set"
{% endif %}

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

{% block where %}
WHERE 1=1
{% if theme_id and theme_id != 'all' %}
AND "filter_rs"."theme_id" = {{ theme_id }}
{% endif %}
{% if year and year != 'all' %}
AND "filter_rs"."year" = {{ year }}
{% endif %}
{% if search_query %}
AND (LOWER("rebrickable_minifigures"."name") LIKE LOWER('%{{ search_query }}%'))
{% endif %}
{% endblock %}

{% block having %}
{% if problems_filter %}
HAVING 1=1
{% if problems_filter == 'missing' %}
AND SUM(IFNULL("problem_join"."total_missing", 0)) > 0
{% elif problems_filter == 'damaged' %}
AND SUM(IFNULL("problem_join"."total_damaged", 0)) > 0
{% elif problems_filter == 'both' %}
AND SUM(IFNULL("problem_join"."total_missing", 0)) > 0 AND SUM(IFNULL("problem_join"."total_damaged", 0)) > 0
{% endif %}
{% endif %}
{% endblock %}

{% block group %}
GROUP BY
    "rebrickable_minifigures"."figure"
{% endblock %}
