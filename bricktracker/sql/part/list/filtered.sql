{#
  The one filtered parts list. Used by /parts and by /parts/problem, which passes
  problem_only.

  Filters: owner, color, theme, year, storage, tag, status, plus search, spare parts
  and individuals only. Every one of them is a single WHERE condition. There is no
  CASE inside the aggregates on purpose: WHERE runs before GROUP BY, so a row that
  fails a filter never reaches the SUM in the first place.

  Joins are pulled in only when a filter actually needs them, so an unfiltered page
  costs the same as it did before.

  owner, status and tag become column names, so they cannot be bound as parameters.
  The view validates them against the known metadata ids before they get here.
#}
{% extends 'part/base/base.sql' %}

{% block total_missing %}
SUM("combined"."missing") AS "total_missing",
{% endblock %}

{% block total_damaged %}
SUM("combined"."damaged") AS "total_damaged",
{% endblock %}

{% block total_quantity %}
SUM("combined"."quantity" * IFNULL("minifigure_quantities"."quantity", 1)) AS "total_quantity",
{% endblock %}

{% block total_sets %}
IFNULL(COUNT(DISTINCT CASE WHEN "combined"."source_type" = 'set' THEN "combined"."id" ELSE NULL END), 0) AS "total_sets",
{% endblock %}

{% block total_minifigures %}
SUM(IFNULL("minifigure_quantities"."quantity", 0)) AS "total_minifigures"
{% endblock %}

{% block join %}
-- Minifigure quantities, from set minifigures and individual ones alike
LEFT JOIN (
    SELECT
        "bricktracker_minifigures"."id",
        "bricktracker_minifigures"."figure",
        "bricktracker_minifigures"."quantity"
    FROM "bricktracker_minifigures"

    UNION ALL

    SELECT
        "bricktracker_individual_minifigures"."id",
        "bricktracker_individual_minifigures"."figure",
        "bricktracker_individual_minifigures"."quantity"
    FROM "bricktracker_individual_minifigures"
) AS "minifigure_quantities"
ON "combined"."id" IS NOT DISTINCT FROM "minifigure_quantities"."id"
AND "combined"."figure" IS NOT DISTINCT FROM "minifigure_quantities"."figure"

{% if theme_id or year or storage_id %}
-- Sets, for theme, year and set level storage
LEFT JOIN "bricktracker_sets"
ON "combined"."source_type" = 'set'
AND "combined"."id" IS NOT DISTINCT FROM "bricktracker_sets"."id"
{% endif %}

{% if theme_id or year %}
LEFT JOIN "rebrickable_sets"
ON "bricktracker_sets"."set" IS NOT DISTINCT FROM "rebrickable_sets"."set"
{% endif %}

{% if storage_id %}
-- Individual minifigures carry their own storage
LEFT JOIN "bricktracker_individual_minifigures"
ON "combined"."source_type" = 'individual_minifigure'
AND "combined"."id" IS NOT DISTINCT FROM "bricktracker_individual_minifigures"."id"
{% endif %}

{% if storage_id or owner_id %}
-- Individual parts, and the lot they may belong to. A part with no storage or owner
-- of its own inherits the lot's.
LEFT JOIN "bricktracker_individual_parts"
ON "combined"."source_type" = 'individual_part'
AND "combined"."id" IS NOT DISTINCT FROM "bricktracker_individual_parts"."id"

LEFT JOIN "bricktracker_individual_part_lots"
ON "bricktracker_individual_parts"."lot_id" IS NOT DISTINCT FROM "bricktracker_individual_part_lots"."id"
{% endif %}

{% if owner_id %}
-- Owners, statuses and tags all live in the set metadata tables keyed by item id,
-- shared by sets, individual minifigures and individual parts, so no source check.
LEFT JOIN "bricktracker_set_owners"
ON "combined"."id" IS NOT DISTINCT FROM "bricktracker_set_owners"."id"

LEFT JOIN "bricktracker_set_owners" AS "lot_owners"
ON "bricktracker_individual_part_lots"."id" IS NOT DISTINCT FROM "lot_owners"."id"
{% endif %}

{% if status_id %}
LEFT JOIN "bricktracker_set_statuses"
ON "combined"."id" IS NOT DISTINCT FROM "bricktracker_set_statuses"."id"
{% endif %}

{% if tag_id %}
LEFT JOIN "bricktracker_set_tags"
ON "combined"."id" IS NOT DISTINCT FROM "bricktracker_set_tags"."id"
{% endif %}
{% endblock %}

{% block where %}
{% set conditions = [] %}

{% if problem_only %}
  {% set _ = conditions.append('("combined"."missing" > 0 OR "combined"."damaged" > 0)') %}
{% endif %}

{% if skip_spare_parts %}
  {% set _ = conditions.append('"combined"."spare" = 0') %}
{% endif %}

{% if individuals_filter %}
  {% set _ = conditions.append('"combined"."source_type" = \'individual_part\'') %}
{% endif %}

{% if color_id %}
  {% set _ = conditions.append('"combined"."color" = :color_id') %}
{% endif %}

{% if search_query %}
  {% set _ = conditions.append('(LOWER("rebrickable_parts"."name") LIKE :search_query OR LOWER("rebrickable_parts"."color_name") LIKE :search_query OR LOWER("combined"."part") LIKE :search_query)') %}
{% endif %}

{# Theme and year only exist for set sourced parts. The LEFT JOIN gives NULL for
   everything else, and NULL = x is never true, so individual parts drop out on
   their own. #}
{% if theme_id %}
  {% set _ = conditions.append('"rebrickable_sets"."theme_id" = :theme_id') %}
{% endif %}

{% if year %}
  {% set _ = conditions.append('"rebrickable_sets"."year" = :year') %}
{% endif %}

{% if storage_id %}
  {% set storage_value = 'COALESCE("bricktracker_sets"."storage", "bricktracker_individual_minifigures"."storage", "bricktracker_individual_parts"."storage", "bricktracker_individual_part_lots"."storage")' %}
  {% if storage_id == '__none__' %}
    {% set _ = conditions.append(storage_value ~ ' IS NULL') %}
  {% elif storage_id == '-__none__' %}
    {% set _ = conditions.append(storage_value ~ ' IS NOT NULL') %}
  {% elif storage_id.startswith('-') %}
    {# IS NOT rather than <> so parts with no storage at all still count as "not this one" #}
    {% set _ = conditions.append(storage_value ~ ' IS NOT :storage_id') %}
  {% else %}
    {% set _ = conditions.append(storage_value ~ ' IS :storage_id') %}
  {% endif %}
{% endif %}

{% if owner_id %}
  {% if owner_id.startswith('-') %}
    {% set _ = conditions.append('(IFNULL("bricktracker_set_owners"."owner_' ~ owner_id[1:] ~ '", 0) = 0 AND IFNULL("lot_owners"."owner_' ~ owner_id[1:] ~ '", 0) = 0)') %}
  {% else %}
    {% set _ = conditions.append('("bricktracker_set_owners"."owner_' ~ owner_id ~ '" = 1 OR "lot_owners"."owner_' ~ owner_id ~ '" = 1)') %}
  {% endif %}
{% endif %}

{# Negated forms use IFNULL so an item with no metadata row counts as not having the
   status or tag, which is what "everything except assembled" means. #}
{% if status_id %}
  {% if status_id.startswith('-') %}
    {% set _ = conditions.append('IFNULL("bricktracker_set_statuses"."status_' ~ status_id[1:] ~ '", 0) = 0') %}
  {% else %}
    {% set _ = conditions.append('"bricktracker_set_statuses"."status_' ~ status_id ~ '" = 1') %}
  {% endif %}
{% endif %}

{% if tag_id %}
  {% if tag_id.startswith('-') %}
    {% set _ = conditions.append('IFNULL("bricktracker_set_tags"."tag_' ~ tag_id[1:] ~ '", 0) = 0') %}
  {% else %}
    {% set _ = conditions.append('"bricktracker_set_tags"."tag_' ~ tag_id ~ '" = 1') %}
  {% endif %}
{% endif %}

{% if conditions %}
WHERE {{ conditions | join(' AND ') }}
{% endif %}
{% endblock %}

{% block group %}
GROUP BY
    "combined"."part",
    "combined"."color",
    "combined"."spare"
{% endblock %}
