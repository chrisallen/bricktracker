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

-- Join with rebrickable sets for theme/year filtering
INNER JOIN "rebrickable_sets"
ON "bricktracker_sets"."set" IS NOT DISTINCT FROM "rebrickable_sets"."set"

-- Left join with set owners (using dynamic columns)
LEFT JOIN "bricktracker_set_owners"
ON "bricktracker_sets"."id" IS NOT DISTINCT FROM "bricktracker_set_owners"."id"

-- Left join with set tags (for tag filtering)
{% if tag_id and tag_id != 'all' %}
LEFT JOIN "bricktracker_set_tags"
ON "bricktracker_sets"."id" IS NOT DISTINCT FROM "bricktracker_set_tags"."id"
{% endif %}

-- Left join with minifigures
LEFT JOIN "bricktracker_minifigures"
ON "bricktracker_parts"."id" IS NOT DISTINCT FROM "bricktracker_minifigures"."id"
AND "bricktracker_parts"."figure" IS NOT DISTINCT FROM "bricktracker_minifigures"."figure"
{% endblock %}

{% block where %}
{% set conditions = [] %}
-- Always filter for problematic parts
{% set _ = conditions.append('("bricktracker_parts"."missing" > 0 OR "bricktracker_parts"."damaged" > 0)') %}
{% if owner_id and owner_id != 'all' %}
  {% set _ = conditions.append('"bricktracker_set_owners"."owner_' ~ owner_id ~ '" = 1') %}
{% endif %}
{% if color_id and color_id != 'all' %}
  {% set _ = conditions.append('"bricktracker_parts"."color" = ' ~ color_id) %}
{% endif %}
{% if theme_id and theme_id != 'all' %}
  {% set _ = conditions.append('"rebrickable_sets"."theme_id" = ' ~ theme_id) %}
{% endif %}
{% if year and year != 'all' %}
  {% set _ = conditions.append('"rebrickable_sets"."year" = ' ~ year) %}
{% endif %}
{% if storage_id and storage_id != 'all' %}
  {% set _ = conditions.append('"bricktracker_sets"."storage" = \'' ~ storage_id ~ '\'') %}
{% endif %}
{% if tag_id and tag_id != 'all' %}
  {% set _ = conditions.append('"bricktracker_set_tags"."tag_' ~ tag_id ~ '" = 1') %}
{% endif %}
{% if search_query %}
  {% set search_condition = '(LOWER("rebrickable_parts"."name") LIKE LOWER(\'%' ~ search_query ~ '%\') OR LOWER("rebrickable_parts"."color_name") LIKE LOWER(\'%' ~ search_query ~ '%\') OR LOWER("bricktracker_parts"."part") LIKE LOWER(\'%' ~ search_query ~ '%\'))' %}
  {% set _ = conditions.append(search_condition) %}
{% endif %}
{% if skip_spare_parts %}
  {% set _ = conditions.append('"bricktracker_parts"."spare" = 0') %}
{% endif %}
WHERE {{ conditions | join(' AND ') }}
{% endblock %}

{% block group %}
GROUP BY
    "bricktracker_parts"."part",
    "bricktracker_parts"."color",
    "bricktracker_parts"."spare"
{% endblock %}
