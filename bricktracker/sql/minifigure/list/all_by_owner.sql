{% extends 'minifigure/base/base.sql' %}

{% block total_missing %}
SUM(IFNULL("problem_join"."total_missing", 0)) AS "total_missing",
{% endblock %}

{% block total_damaged %}
SUM(IFNULL("problem_join"."total_damaged", 0)) AS "total_damaged",
{% endblock %}

{% block total_quantity %}
{% if owner_id and owner_id != 'all' %}
SUM(CASE WHEN "bricktracker_set_owners"."owner_{{ owner_id }}" = 1 THEN IFNULL("bricktracker_minifigures"."quantity", 0) ELSE 0 END) AS "total_quantity",
{% else %}
SUM(IFNULL("bricktracker_minifigures"."quantity", 0)) AS "total_quantity",
{% endif %}
{% endblock %}

{% block total_sets %}
{% if owner_id and owner_id != 'all' %}
COUNT(CASE WHEN "bricktracker_set_owners"."owner_{{ owner_id }}" = 1 THEN "bricktracker_minifigures"."id" ELSE NULL END) AS "total_sets"
{% else %}
COUNT("bricktracker_minifigures"."id") AS "total_sets"
{% endif %}
{% endblock %}

{% block join %}
-- Join with sets to get owner information
INNER JOIN "bricktracker_sets"
ON "bricktracker_minifigures"."id" IS NOT DISTINCT FROM "bricktracker_sets"."id"

-- Left join with set owners (using dynamic columns)
LEFT JOIN "bricktracker_set_owners"
ON "bricktracker_sets"."id" IS NOT DISTINCT FROM "bricktracker_set_owners"."id"

-- LEFT JOIN + SELECT to avoid messing the total
LEFT JOIN (
    SELECT
        "bricktracker_parts"."id",
        "bricktracker_parts"."figure",
        {% if owner_id and owner_id != 'all' %}
        SUM(CASE WHEN "owner_parts"."owner_{{ owner_id }}" = 1 THEN "bricktracker_parts"."missing" ELSE 0 END) AS "total_missing",
        SUM(CASE WHEN "owner_parts"."owner_{{ owner_id }}" = 1 THEN "bricktracker_parts"."damaged" ELSE 0 END) AS "total_damaged"
        {% else %}
        SUM("bricktracker_parts"."missing") AS "total_missing",
        SUM("bricktracker_parts"."damaged") AS "total_damaged"
        {% endif %}
    FROM "bricktracker_parts"
    INNER JOIN "bricktracker_sets" AS "parts_sets"
    ON "bricktracker_parts"."id" IS NOT DISTINCT FROM "parts_sets"."id"
    LEFT JOIN "bricktracker_set_owners" AS "owner_parts"
    ON "parts_sets"."id" IS NOT DISTINCT FROM "owner_parts"."id"
    WHERE "bricktracker_parts"."figure" IS NOT NULL
    GROUP BY
        "bricktracker_parts"."id",
        "bricktracker_parts"."figure"
) "problem_join"
ON "bricktracker_minifigures"."id" IS NOT DISTINCT FROM "problem_join"."id"
AND "rebrickable_minifigures"."figure" IS NOT DISTINCT FROM "problem_join"."figure"
{% endblock %}

{% block where %}
{% if owner_id and owner_id != 'all' %}
WHERE "bricktracker_set_owners"."owner_{{ owner_id }}" = 1
{% endif %}
{% endblock %}

{% block group %}
GROUP BY
    "rebrickable_minifigures"."figure"
{% endblock %}