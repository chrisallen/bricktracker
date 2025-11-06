{% extends 'part/base/base.sql' %}

{% block total_missing %}
SUM("bricktracker_parts"."missing") AS "total_missing",
{% endblock %}

{% block total_damaged %}
SUM("bricktracker_parts"."damaged") AS "total_damaged",
{% endblock %}

{% block total_quantity %}
SUM("bricktracker_parts"."quantity" * IFNULL("bricktracker_minifigures"."quantity", 1)) AS "total_quantity",
{% endblock %}

{% block total_sets %}
IFNULL(COUNT(DISTINCT "bricktracker_parts"."id"), 0) AS "total_sets",
{% endblock %}

{% block total_minifigures %}
SUM(IFNULL("bricktracker_minifigures"."quantity", 0)) AS "total_minifigures"
{% endblock %}

{% block join %}
LEFT JOIN "bricktracker_minifigures"
ON "bricktracker_parts"."id" IS NOT DISTINCT FROM "bricktracker_minifigures"."id"
AND "bricktracker_parts"."figure" IS NOT DISTINCT FROM "bricktracker_minifigures"."figure"

{% if theme_id or year %}
INNER JOIN "bricktracker_sets" AS "filter_sets"
ON "bricktracker_parts"."id" IS NOT DISTINCT FROM "filter_sets"."id"
INNER JOIN "rebrickable_sets" AS "filter_rs"
ON "filter_sets"."set" IS NOT DISTINCT FROM "filter_rs"."set"
{% endif %}
{% endblock %}

{% block where %}
{% set conditions = [] %}
{% if color_id and color_id != 'all' %}
  {% set _ = conditions.append('"bricktracker_parts"."color" = ' ~ color_id) %}
{% endif %}
{% if theme_id and theme_id != 'all' %}
  {% set _ = conditions.append('"filter_rs"."theme_id" = ' ~ theme_id) %}
{% endif %}
{% if year and year != 'all' %}
  {% set _ = conditions.append('"filter_rs"."year" = ' ~ year) %}
{% endif %}
{% if search_query %}
  {% set search_condition = '(LOWER("rebrickable_parts"."name") LIKE LOWER(\'%' ~ search_query ~ '%\') OR LOWER("rebrickable_parts"."color_name") LIKE LOWER(\'%' ~ search_query ~ '%\') OR LOWER("bricktracker_parts"."part") LIKE LOWER(\'%' ~ search_query ~ '%\'))' %}
  {% set _ = conditions.append(search_condition) %}
{% endif %}
{% if skip_spare_parts %}
  {% set _ = conditions.append('"bricktracker_parts"."spare" = 0') %}
{% endif %}
{% if conditions %}
WHERE {{ conditions | join(' AND ') }}
{% endif %}
{% endblock %}

{% block group %}
GROUP BY
    "bricktracker_parts"."part",
    "bricktracker_parts"."color",
    "bricktracker_parts"."spare"
{% endblock %}
