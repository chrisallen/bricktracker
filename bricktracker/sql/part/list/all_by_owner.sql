{% extends 'part/base/base.sql' %}

{% block total_missing %}
{% if owner_id and owner_id != 'all' %}
SUM(CASE WHEN "bricktracker_set_owners"."owner_{{ owner_id }}" = 1 THEN "bricktracker_parts"."missing" ELSE 0 END) AS "total_missing",
{% else %}
SUM("bricktracker_parts"."missing") AS "total_missing",
{% endif %}
{% endblock %}

{% block total_damaged %}
{% if owner_id and owner_id != 'all' %}
SUM(CASE WHEN "bricktracker_set_owners"."owner_{{ owner_id }}" = 1 THEN "bricktracker_parts"."damaged" ELSE 0 END) AS "total_damaged",
{% else %}
SUM("bricktracker_parts"."damaged") AS "total_damaged",
{% endif %}
{% endblock %}

{% block total_quantity %}
{% if owner_id and owner_id != 'all' %}
SUM(CASE WHEN "bricktracker_set_owners"."owner_{{ owner_id }}" = 1 THEN "bricktracker_parts"."quantity" * IFNULL("bricktracker_minifigures"."quantity", 1) ELSE 0 END) AS "total_quantity",
{% else %}
SUM("bricktracker_parts"."quantity" * IFNULL("bricktracker_minifigures"."quantity", 1)) AS "total_quantity",
{% endif %}
{% endblock %}

{% block total_sets %}
{% if owner_id and owner_id != 'all' %}
COUNT(DISTINCT CASE WHEN "bricktracker_set_owners"."owner_{{ owner_id }}" = 1 THEN "bricktracker_parts"."id" ELSE NULL END) AS "total_sets",
{% else %}
COUNT(DISTINCT "bricktracker_parts"."id") AS "total_sets",
{% endif %}
{% endblock %}

{% block total_minifigures %}
{% if owner_id and owner_id != 'all' %}
SUM(CASE WHEN "bricktracker_set_owners"."owner_{{ owner_id }}" = 1 THEN IFNULL("bricktracker_minifigures"."quantity", 0) ELSE 0 END) AS "total_minifigures"
{% else %}
SUM(IFNULL("bricktracker_minifigures"."quantity", 0)) AS "total_minifigures"
{% endif %}
{% endblock %}

{% block join %}
-- Join with sets to get owner information
INNER JOIN "bricktracker_sets"
ON "bricktracker_parts"."id" IS NOT DISTINCT FROM "bricktracker_sets"."id"

-- Left join with set owners (using dynamic columns)
LEFT JOIN "bricktracker_set_owners"
ON "bricktracker_sets"."id" IS NOT DISTINCT FROM "bricktracker_set_owners"."id"

-- Left join with minifigures
LEFT JOIN "bricktracker_minifigures"
ON "bricktracker_parts"."id" IS NOT DISTINCT FROM "bricktracker_minifigures"."id"
AND "bricktracker_parts"."figure" IS NOT DISTINCT FROM "bricktracker_minifigures"."figure"
{% endblock %}

{% block where %}
{% set has_where = false %}
{% if owner_id and owner_id != 'all' %}
WHERE "bricktracker_set_owners"."owner_{{ owner_id }}" = 1
{% set has_where = true %}
{% endif %}
{% if color_id and color_id != 'all' %}
{% if has_where %}
AND "bricktracker_parts"."color" = {{ color_id }}
{% else %}
WHERE "bricktracker_parts"."color" = {{ color_id }}
{% endif %}
{% endif %}
{% endblock %}

{% block group %}
GROUP BY
    "bricktracker_parts"."part",
    "bricktracker_parts"."color",
    "bricktracker_parts"."spare"
{% endblock %}