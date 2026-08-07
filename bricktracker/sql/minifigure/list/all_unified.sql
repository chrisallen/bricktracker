{#
  Unified query that shows both set minifigures and individual minifigures.

  theme_id, year and search_query are data, not column names, so they are bound
  (:theme_id, :year, :search_query) rather than interpolated into the query text. A
  leading "-" means "not this"; the view strips it before binding the value, this
  template only uses it to pick the SQL operator.

  Individual minifigures aren't tied to any set, so they have no theme, year or
  custom field value of their own. When one of those filters is active they drop out
  entirely, same reasoning as parts use for the same case.
#}
SELECT
    "figure",
    "number",
    "number_of_parts",
    "name",
    "image",
    SUM("quantity") AS "quantity",
    SUM("total_missing") AS "total_missing",
    SUM("total_damaged") AS "total_damaged",
    SUM("total_quantity") AS "total_quantity",
    SUM("total_sets") AS "total_sets"
FROM (
    -- Set minifigures
    SELECT
        "rebrickable_minifigures"."figure",
        "rebrickable_minifigures"."number",
        "rebrickable_minifigures"."number_of_parts",
        "rebrickable_minifigures"."name",
        "rebrickable_minifigures"."image",
        "bricktracker_minifigures"."quantity",
        IFNULL("problem_join"."total_missing", 0) AS "total_missing",
        IFNULL("problem_join"."total_damaged", 0) AS "total_damaged",
        IFNULL("bricktracker_minifigures"."quantity", 0) AS "total_quantity",
        1 AS "total_sets",
        0 AS "total_individual"
    FROM "bricktracker_minifigures"
    INNER JOIN "rebrickable_minifigures"
    ON "bricktracker_minifigures"."figure" IS NOT DISTINCT FROM "rebrickable_minifigures"."figure"
    {% if theme_id or year or custom_field_filters %}
    -- Join with sets for theme/year/custom field filtering
    INNER JOIN "bricktracker_sets" AS "filter_sets"
    ON "bricktracker_minifigures"."id" IS NOT DISTINCT FROM "filter_sets"."id"
    INNER JOIN "rebrickable_sets" AS "filter_rs"
    ON "filter_sets"."set" IS NOT DISTINCT FROM "filter_rs"."set"
    {% endif %}
    {% if custom_field_filters %}
    LEFT JOIN "bricktracker_set_custom_fields"
    ON "filter_sets"."id" IS NOT DISTINCT FROM "bricktracker_set_custom_fields"."id"
    {% endif %}
    -- LEFT JOIN for problems
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
    WHERE 1=1
    {% if theme_id %}
    {% if theme_id.startswith('-') %}
    AND "filter_rs"."theme_id" != :theme_id
    {% else %}
    AND "filter_rs"."theme_id" = :theme_id
    {% endif %}
    {% endif %}
    {% if year %}
    {% if year.startswith('-') %}
    AND "filter_rs"."year" != :year
    {% else %}
    AND "filter_rs"."year" = :year
    {% endif %}
    {% endif %}
    {% for field_id, value in (custom_field_filters or {}).items() %}
    {% if value.startswith('-') %}
    AND IFNULL("bricktracker_set_custom_fields"."custom_field_{{ field_id }}", '') != :custom_field_value_{{ field_id }}
    {% else %}
    AND "bricktracker_set_custom_fields"."custom_field_{{ field_id }}" = :custom_field_value_{{ field_id }}
    {% endif %}
    {% endfor %}
    {% if search_query %}
    AND (LOWER("rebrickable_minifigures"."name") LIKE :search_query)
    {% endif %}

    UNION ALL

    -- Individual minifigures
    SELECT
        "rebrickable_minifigures"."figure",
        "rebrickable_minifigures"."number",
        "rebrickable_minifigures"."number_of_parts",
        "rebrickable_minifigures"."name",
        "rebrickable_minifigures"."image",
        "bricktracker_individual_minifigures"."quantity",
        IFNULL("ind_problem_join"."total_missing", 0) AS "total_missing",
        IFNULL("ind_problem_join"."total_damaged", 0) AS "total_damaged",
        IFNULL("bricktracker_individual_minifigures"."quantity", 0) AS "total_quantity",
        0 AS "total_sets",
        1 AS "total_individual"
    FROM "bricktracker_individual_minifigures"
    INNER JOIN "rebrickable_minifigures"
    ON "bricktracker_individual_minifigures"."figure" IS NOT DISTINCT FROM "rebrickable_minifigures"."figure"
    -- LEFT JOIN for individual minifigure problems
    LEFT JOIN (
        SELECT
            "bricktracker_individual_minifigure_parts"."id",
            SUM("bricktracker_individual_minifigure_parts"."missing") AS "total_missing",
            SUM("bricktracker_individual_minifigure_parts"."damaged") AS "total_damaged"
        FROM "bricktracker_individual_minifigure_parts"
        GROUP BY "bricktracker_individual_minifigure_parts"."id"
    ) "ind_problem_join"
    ON "bricktracker_individual_minifigures"."id" IS NOT DISTINCT FROM "ind_problem_join"."id"
    WHERE 1=1
    {% if theme_id or year or custom_field_filters %}
    -- No set behind an individual minifigure, so it has no theme, year or custom
    -- field value: it can never match a filter on any of those.
    AND 0=1
    {% endif %}
    {% if search_query %}
    AND (LOWER("rebrickable_minifigures"."name") LIKE :search_query)
    {% endif %}
) "combined"
GROUP BY
    "figure",
    "number",
    "number_of_parts",
    "name",
    "image"
{% if problems_filter or individuals_filter %}
HAVING 1=1
{% if problems_filter == 'missing' %}
AND SUM("total_missing") > 0
{% elif problems_filter == 'damaged' %}
AND SUM("total_damaged") > 0
{% elif problems_filter == 'both' %}
AND SUM("total_missing") > 0 AND SUM("total_damaged") > 0
{% endif %}
{% if individuals_filter == 'only' %}
AND SUM("total_individual") > 0
{% elif individuals_filter == 'exclude' %}
AND SUM("total_sets") > 0
{% endif %}
{% endif %}

{% if order %}
ORDER BY {{ order.replace('"rebrickable_minifigures"."', '"') }}
{% endif %}

{% if limit %}
LIMIT {{ limit }}
{% endif %}

{% if offset %}
OFFSET {{ offset }}
{% endif %}
