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
    MAX("bricktracker_sets"."purchase_date") AS "purchase_date_max",
    REPLACE(GROUP_CONCAT(DISTINCT "bricktracker_sets"."purchase_location"), ',', '|') AS "purchase_location",
    ROUND(AVG("bricktracker_sets"."purchase_price"), 1) AS "purchase_price",
    (SELECT "description" FROM "bricktracker_sets" WHERE "set" = "rebrickable_sets"."set" LIMIT 1) AS "description"
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
    {% block custom_fields %}
        {% if custom_fields_dict %}
            {% for column, uuid in custom_fields_dict.items() %}
                -- Representative value for the group (shared value when all
                -- instances agree; used for bulk-edit read across instances).
                , MAX("bricktracker_set_custom_fields"."{{ column }}") AS "{{ column }}"
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

{% if custom_fields_dict %}
LEFT JOIN "bricktracker_set_custom_fields"
ON "bricktracker_sets"."id" IS NOT DISTINCT FROM "bricktracker_set_custom_fields"."id"
{% endif %}

{% block where %}
WHERE 1=1
{% if search_query %}
AND (LOWER("rebrickable_sets"."name") LIKE LOWER('%{{ search_query }}%')
   OR LOWER("rebrickable_sets"."set") LIKE LOWER('%{{ search_query }}%'))
{% endif %}

{% if theme_filter %}
{% if theme_filter is string and theme_filter.startswith('-') %}
AND "rebrickable_sets"."theme_id" != {{ theme_filter[1:] }}
{% else %}
AND "rebrickable_sets"."theme_id" = {{ theme_filter }}
{% endif %}
{% endif %}

{% if year_filter %}
{% if year_filter is string and year_filter.startswith('-') %}
AND "rebrickable_sets"."year" != {{ year_filter[1:] }}
{% else %}
AND "rebrickable_sets"."year" = {{ year_filter }}
{% endif %}
{% endif %}

{% if storage_filter %}
{% if storage_filter == '__none__' %}
AND EXISTS (
    SELECT 1 FROM "bricktracker_sets" bs_filter
    WHERE bs_filter."set" = "rebrickable_sets"."set"
    AND (bs_filter."storage" IS NULL OR bs_filter."storage" = '')
)
{% elif storage_filter == '-__none__' %}
AND NOT EXISTS (
    SELECT 1 FROM "bricktracker_sets" bs_filter
    WHERE bs_filter."set" = "rebrickable_sets"."set"
    AND (bs_filter."storage" IS NULL OR bs_filter."storage" = '')
)
{% elif storage_filter.startswith('-') %}
AND NOT EXISTS (
    SELECT 1 FROM "bricktracker_sets" bs_filter
    WHERE bs_filter."set" = "rebrickable_sets"."set"
    AND bs_filter."storage" = '{{ storage_filter[1:] }}'
)
{% else %}
AND EXISTS (
    SELECT 1 FROM "bricktracker_sets" bs_filter
    WHERE bs_filter."set" = "rebrickable_sets"."set"
    AND bs_filter."storage" = '{{ storage_filter }}'
)
{% endif %}
{% endif %}

{% if purchase_location_filter %}
{% if purchase_location_filter == '__none__' %}
AND EXISTS (
    SELECT 1 FROM "bricktracker_sets" bs_filter
    WHERE bs_filter."set" = "rebrickable_sets"."set"
    AND (bs_filter."purchase_location" IS NULL OR bs_filter."purchase_location" = '')
)
{% elif purchase_location_filter == '-__none__' %}
AND NOT EXISTS (
    SELECT 1 FROM "bricktracker_sets" bs_filter
    WHERE bs_filter."set" = "rebrickable_sets"."set"
    AND (bs_filter."purchase_location" IS NULL OR bs_filter."purchase_location" = '')
)
{% elif purchase_location_filter.startswith('-') %}
AND NOT EXISTS (
    SELECT 1 FROM "bricktracker_sets" bs_filter
    WHERE bs_filter."set" = "rebrickable_sets"."set"
    AND bs_filter."purchase_location" = '{{ purchase_location_filter[1:] }}'
)
{% else %}
AND EXISTS (
    SELECT 1 FROM "bricktracker_sets" bs_filter
    WHERE bs_filter."set" = "rebrickable_sets"."set"
    AND bs_filter."purchase_location" = '{{ purchase_location_filter }}'
)
{% endif %}
{% endif %}

{# Owner and tag used to be missing here, which forced the whole page off the
   consolidated query: picking an owner silently turned grouped cards into
   per instance cards. Same EXISTS shape as storage above, so a group shows when any
   of its instances matches. #}
{% if owner_filter %}
{% if owner_filter.startswith('-owner-') %}
AND NOT EXISTS (
    SELECT 1 FROM "bricktracker_sets" bs_filter
    INNER JOIN "bricktracker_set_owners" bso_filter
    ON bs_filter."id" IS NOT DISTINCT FROM bso_filter."id"
    WHERE bs_filter."set" = "rebrickable_sets"."set"
    AND bso_filter."{{ owner_filter[1:].replace('-', '_') }}" = 1
)
{% elif owner_filter.startswith('owner-') %}
AND EXISTS (
    SELECT 1 FROM "bricktracker_sets" bs_filter
    INNER JOIN "bricktracker_set_owners" bso_filter
    ON bs_filter."id" IS NOT DISTINCT FROM bso_filter."id"
    WHERE bs_filter."set" = "rebrickable_sets"."set"
    AND bso_filter."{{ owner_filter.replace('-', '_') }}" = 1
)
{% endif %}
{% endif %}

{% if tag_filter %}
{% if tag_filter.startswith('-tag-') %}
AND NOT EXISTS (
    SELECT 1 FROM "bricktracker_sets" bs_filter
    INNER JOIN "bricktracker_set_tags" bst_filter
    ON bs_filter."id" IS NOT DISTINCT FROM bst_filter."id"
    WHERE bs_filter."set" = "rebrickable_sets"."set"
    AND bst_filter."{{ tag_filter[1:].replace('-', '_') }}" = 1
)
{% elif tag_filter.startswith('tag-') %}
AND EXISTS (
    SELECT 1 FROM "bricktracker_sets" bs_filter
    INNER JOIN "bricktracker_set_tags" bst_filter
    ON bs_filter."id" IS NOT DISTINCT FROM bst_filter."id"
    WHERE bs_filter."set" = "rebrickable_sets"."set"
    AND bst_filter."{{ tag_filter.replace('-', '_') }}" = 1
)
{% endif %}
{% endif %}

{% if parts_min %}
AND "rebrickable_sets"."number_of_parts" >= {{ parts_min }}
{% endif %}

{% if parts_max %}
AND "rebrickable_sets"."number_of_parts" <= {{ parts_max }}
{% endif %}

{% if year_min %}
AND "rebrickable_sets"."year" >= {{ year_min }}
{% endif %}

{% if year_max %}
AND "rebrickable_sets"."year" <= {{ year_max }}
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

{# Custom field values are free text, so unlike owner/tag/status (booleans) they are
   bound (:custom_field_value_<id>) rather than interpolated. Only the column name
   (the field id) is interpolated, and it never comes from user input directly. #}
{% for field_id, value in (custom_field_filters or {}).items() %}
{% if value.startswith('-') %}
AND NOT EXISTS (
    SELECT 1 FROM "bricktracker_sets" bs_filter
    INNER JOIN "bricktracker_set_custom_fields" bscf_filter
    ON bs_filter."id" IS NOT DISTINCT FROM bscf_filter."id"
    WHERE bs_filter."set" = "rebrickable_sets"."set"
    AND bscf_filter."custom_field_{{ field_id }}" = :custom_field_value_{{ field_id }}
)
{% else %}
AND EXISTS (
    SELECT 1 FROM "bricktracker_sets" bs_filter
    INNER JOIN "bricktracker_set_custom_fields" bscf_filter
    ON bs_filter."id" IS NOT DISTINCT FROM bscf_filter."id"
    WHERE bs_filter."set" = "rebrickable_sets"."set"
    AND bscf_filter."custom_field_{{ field_id }}" = :custom_field_value_{{ field_id }}
)
{% endif %}
{% endfor %}
{% endblock %}

GROUP BY "rebrickable_sets"."set"

{% if status_filter or duplicate_filter %}
HAVING 1=1
{% if status_filter %}
{% if status_filter == 'has-missing' %}
AND IFNULL(SUM("problem_join"."total_missing"), 0) > 0
{% elif status_filter == '-has-missing' %}
AND IFNULL(SUM("problem_join"."total_missing"), 0) = 0
{% elif status_filter == 'has-damaged' %}
AND IFNULL(SUM("problem_join"."total_damaged"), 0) > 0
{% elif status_filter == '-has-damaged' %}
AND IFNULL(SUM("problem_join"."total_damaged"), 0) = 0
{% endif %}
{% endif %}
{% if duplicate_filter %}
AND COUNT("bricktracker_sets"."id") > 1
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