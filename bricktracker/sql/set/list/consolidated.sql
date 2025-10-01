SELECT
    (SELECT MIN("id") FROM "bricktracker_sets" WHERE "set" = "rebrickable_sets"."set") AS "id",
    "rebrickable_sets"."set",
    "rebrickable_sets"."number",
    "rebrickable_sets"."version",
    "rebrickable_sets"."name",
    "rebrickable_sets"."year",
    "rebrickable_sets"."theme_id",
    "rebrickable_sets"."number_of_parts",
    "rebrickable_sets"."image",
    "rebrickable_sets"."url",
    COUNT("bricktracker_sets"."id") AS "instance_count",
    IFNULL(SUM("problem_join"."total_missing"), 0) AS "total_missing",
    IFNULL(SUM("problem_join"."total_damaged"), 0) AS "total_damaged",
    IFNULL(MAX("minifigures_join"."total"), 0) AS "total_minifigures",
    -- Keep one representative instance for display purposes
    GROUP_CONCAT("bricktracker_sets"."id", '|') AS "instance_ids",
    REPLACE(GROUP_CONCAT(DISTINCT "bricktracker_sets"."storage"), ',', '|') AS "storage",
    MIN("bricktracker_sets"."purchase_date") AS "purchase_date",
    REPLACE(GROUP_CONCAT(DISTINCT "bricktracker_sets"."purchase_location"), ',', '|') AS "purchase_location",
    MIN("bricktracker_sets"."purchase_price") AS "purchase_price"
    {% block owners %}
        {% if owners_dict %}
            {% for column, uuid in owners_dict.items() %}
                , MAX("bricktracker_set_owners"."{{ column }}") AS "{{ column }}"
            {% endfor %}
        {% endif %}
    {% endblock %}
    {% block tags %}
        {% if tags_dict %}
            {% for column, uuid in tags_dict.items() %}
                , MAX("bricktracker_set_tags"."{{ column }}") AS "{{ column }}"
            {% endfor %}
        {% endif %}
    {% endblock %}
    {% block statuses %}
        {% if statuses_dict %}
            {% for column, uuid in statuses_dict.items() %}
                , MAX("bricktracker_set_statuses"."{{ column }}") AS "{{ column }}"
                , IFNULL(SUM("bricktracker_set_statuses"."{{ column }}"), 0) AS "{{ column }}_count"
            {% endfor %}
        {% endif %}
    {% endblock %}
FROM "bricktracker_sets"

INNER JOIN "rebrickable_sets"
ON "bricktracker_sets"."set" IS NOT DISTINCT FROM "rebrickable_sets"."set"

-- LEFT JOIN + SELECT to avoid messing the total
LEFT JOIN (
    SELECT
        "bricktracker_parts"."id",
        SUM("bricktracker_parts"."missing") AS "total_missing",
        SUM("bricktracker_parts"."damaged") AS "total_damaged"
    FROM "bricktracker_parts"
    GROUP BY "bricktracker_parts"."id"
) "problem_join"
ON "bricktracker_sets"."id" IS NOT DISTINCT FROM "problem_join"."id"

-- LEFT JOIN + SELECT to avoid messing the total
LEFT JOIN (
    SELECT
       "bricktracker_minifigures"."id",
       SUM("bricktracker_minifigures"."quantity") AS "total"
    FROM "bricktracker_minifigures"
    GROUP BY "bricktracker_minifigures"."id"
) "minifigures_join"
ON "bricktracker_sets"."id" IS NOT DISTINCT FROM "minifigures_join"."id"

{% if owners_dict %}
LEFT JOIN "bricktracker_set_owners"
ON "bricktracker_sets"."id" IS NOT DISTINCT FROM "bricktracker_set_owners"."id"
{% endif %}

{% if statuses_dict %}
LEFT JOIN "bricktracker_set_statuses"
ON "bricktracker_sets"."id" IS NOT DISTINCT FROM "bricktracker_set_statuses"."id"
{% endif %}

{% if tags_dict %}
LEFT JOIN "bricktracker_set_tags"
ON "bricktracker_sets"."id" IS NOT DISTINCT FROM "bricktracker_set_tags"."id"
{% endif %}

{% block where %}
WHERE 1=1
{% if search_query %}
AND (LOWER("rebrickable_sets"."name") LIKE LOWER('%{{ search_query }}%')
   OR LOWER("rebrickable_sets"."set") LIKE LOWER('%{{ search_query }}%'))
{% endif %}

{% if theme_filter %}
AND "rebrickable_sets"."theme_id" = {{ theme_filter }}
{% endif %}

{% if storage_filter %}
AND EXISTS (
    SELECT 1 FROM "bricktracker_sets" bs_filter
    WHERE bs_filter."set" = "rebrickable_sets"."set"
    AND bs_filter."storage" = '{{ storage_filter }}'
)
{% endif %}

{% if purchase_location_filter %}
AND EXISTS (
    SELECT 1 FROM "bricktracker_sets" bs_filter
    WHERE bs_filter."set" = "rebrickable_sets"."set"
    AND bs_filter."purchase_location" = '{{ purchase_location_filter }}'
)
{% endif %}

{% if status_filter %}
{% if status_filter == 'has-storage' %}
AND EXISTS (
    SELECT 1 FROM "bricktracker_sets" bs_filter
    WHERE bs_filter."set" = "rebrickable_sets"."set"
    AND bs_filter."storage" IS NOT NULL AND bs_filter."storage" != ''
)
{% elif status_filter == '-has-storage' %}
AND NOT EXISTS (
    SELECT 1 FROM "bricktracker_sets" bs_filter
    WHERE bs_filter."set" = "rebrickable_sets"."set"
    AND bs_filter."storage" IS NOT NULL AND bs_filter."storage" != ''
)
{% elif status_filter.startswith('status-') %}
AND EXISTS (
    SELECT 1 FROM "bricktracker_sets" bs_filter
    JOIN "bricktracker_set_statuses" ON bs_filter."id" = "bricktracker_set_statuses"."id"
    WHERE bs_filter."set" = "rebrickable_sets"."set"
    AND "bricktracker_set_statuses"."{{ status_filter.replace('-', '_') }}" = 1
)
{% elif status_filter.startswith('-status-') %}
AND NOT EXISTS (
    SELECT 1 FROM "bricktracker_sets" bs_filter
    JOIN "bricktracker_set_statuses" ON bs_filter."id" = "bricktracker_set_statuses"."id"
    WHERE bs_filter."set" = "rebrickable_sets"."set"
    AND "bricktracker_set_statuses"."{{ status_filter[1:].replace('-', '_') }}" = 1
)
{% endif %}
{% endif %}
{% endblock %}

GROUP BY "rebrickable_sets"."set"

{% if status_filter %}
{% if status_filter == 'has-missing' %}
HAVING IFNULL(SUM("problem_join"."total_missing"), 0) > 0
{% elif status_filter == '-has-missing' %}
HAVING IFNULL(SUM("problem_join"."total_missing"), 0) = 0
{% elif status_filter == 'has-damaged' %}
HAVING IFNULL(SUM("problem_join"."total_damaged"), 0) > 0
{% elif status_filter == '-has-damaged' %}
HAVING IFNULL(SUM("problem_join"."total_damaged"), 0) = 0
{% endif %}
{% endif %}

{% if order %}
ORDER BY {{ order }}
{% endif %}

{% if limit %}
LIMIT {{ limit }}
{% endif %}

{% if offset %}
OFFSET {{ offset }}
{% endif %}