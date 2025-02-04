SELECT
    {% block id %}{% endblock %}
    "bricktracker_sets"."storage",
    "bricktracker_sets"."purchase_date",
    "bricktracker_sets"."purchase_location",
    "bricktracker_sets"."purchase_price",
    "rebrickable_sets"."set",
    "rebrickable_sets"."number",
    "rebrickable_sets"."version",
    "rebrickable_sets"."name",
    "rebrickable_sets"."year",
    "rebrickable_sets"."theme_id",
    "rebrickable_sets"."number_of_parts",
    "rebrickable_sets"."image",
    "rebrickable_sets"."url",
    {% block owners %}
        {% if owners %}{{ owners }},{% endif %}
    {% endblock %}
    {% block tags %}
        {% if tags %}{{ tags }},{% endif %}
    {% endblock %}
    {% block statuses %}
        {% if statuses %}{{ statuses }},{% endif %}
    {% endblock %}
    {% block total_missing %}
    NULL AS "total_missing", -- dummy for order: total_missing
    {% endblock %}
    {% block total_damaged %}
    NULL AS "total_damaged", -- dummy for order: total_damaged
    {% endblock %}
    {% block total_quantity %}
    NULL AS "total_quantity" -- dummy for order: total_quantity
    {% endblock %}
FROM "bricktracker_sets"

INNER JOIN "rebrickable_sets"
ON "bricktracker_sets"."set" IS NOT DISTINCT FROM "rebrickable_sets"."set"

{% block join %}{% endblock %}

{% block where %}{% endblock %}

{% block group %}{% endblock %}

{% if order %}
ORDER BY {{ order }}
{% endif %}

{% if limit %}
LIMIT {{ limit }}
{% endif %}
