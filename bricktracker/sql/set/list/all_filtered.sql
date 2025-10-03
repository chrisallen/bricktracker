{% extends 'set/base/full.sql' %}

{% block where %}
WHERE 1=1
{% if search_query %}
AND (LOWER("rebrickable_sets"."name") LIKE LOWER('%{{ search_query }}%')
   OR LOWER("rebrickable_sets"."set") LIKE LOWER('%{{ search_query }}%'))
{% endif %}

{% if theme_filter %}
AND "rebrickable_sets"."theme_id" = {{ theme_filter }}
{% endif %}

{% if year_filter %}
AND "rebrickable_sets"."year" = {{ year_filter }}
{% endif %}

{% if storage_filter %}
AND "bricktracker_sets"."storage" = '{{ storage_filter }}'
{% endif %}

{% if purchase_location_filter %}
AND "bricktracker_sets"."purchase_location" = '{{ purchase_location_filter }}'
{% endif %}

{% if status_filter %}
{% if status_filter == 'has-missing' %}
AND IFNULL("problem_join"."total_missing", 0) > 0
{% elif status_filter == '-has-missing' %}
AND IFNULL("problem_join"."total_missing", 0) = 0
{% elif status_filter == 'has-damaged' %}
AND IFNULL("problem_join"."total_damaged", 0) > 0
{% elif status_filter == '-has-damaged' %}
AND IFNULL("problem_join"."total_damaged", 0) = 0
{% elif status_filter == 'has-storage' %}
AND "bricktracker_sets"."storage" IS NOT NULL AND "bricktracker_sets"."storage" != ''
{% elif status_filter == '-has-storage' %}
AND ("bricktracker_sets"."storage" IS NULL OR "bricktracker_sets"."storage" = '')
{% elif status_filter.startswith('status-') %}
AND EXISTS (
    SELECT 1 FROM "bricktracker_set_statuses"
    WHERE "bricktracker_set_statuses"."id" = "bricktracker_sets"."id"
    AND "bricktracker_set_statuses"."{{ status_filter.replace('-', '_') }}" = 1
)
{% elif status_filter.startswith('-status-') %}
AND NOT EXISTS (
    SELECT 1 FROM "bricktracker_set_statuses"
    WHERE "bricktracker_set_statuses"."id" = "bricktracker_sets"."id"
    AND "bricktracker_set_statuses"."{{ status_filter[1:].replace('-', '_') }}" = 1
)
{% endif %}
{% endif %}

{% if owner_filter %}
{% if owner_filter.startswith('owner-') %}
AND EXISTS (
    SELECT 1 FROM "bricktracker_set_owners"
    WHERE "bricktracker_set_owners"."id" = "bricktracker_sets"."id"
    AND "bricktracker_set_owners"."{{ owner_filter.replace('-', '_') }}" = 1
)
{% endif %}
{% endif %}

{% if tag_filter %}
{% if tag_filter.startswith('tag-') %}
AND EXISTS (
    SELECT 1 FROM "bricktracker_set_tags"
    WHERE "bricktracker_set_tags"."id" = "bricktracker_sets"."id"
    AND "bricktracker_set_tags"."{{ tag_filter.replace('-', '_') }}" = 1
)
{% endif %}
{% endif %}

{% if duplicate_filter %}
AND (
    SELECT COUNT(*)
    FROM "bricktracker_sets" as "duplicate_check"
    WHERE "duplicate_check"."set" = "bricktracker_sets"."set"
) > 1
{% endif %}
{% endblock %}