SELECT
    "minifigures"."fig_num",
    "minifigures"."set_num",
    "minifigures"."name",
    "minifigures"."quantity",
    "minifigures"."set_img_url",
    "minifigures"."u_id",
    {% block total_missing %}
    NULL AS "total_missing", -- dummy for order: total_missing
    {% endblock %}
    {% block total_quantity %}
    NULL AS "total_quantity", -- dummy for order: total_quantity
    {% endblock %}
    {% block total_sets %}
    NULL AS "total_sets" -- dummy for order: total_sets
    {% endblock %}
FROM "minifigures"

{% block join %}{% endblock %}

{% block where %}{% endblock %}

{% block group %}{% endblock %}

{% if order %}
ORDER BY {{ order }}
{% endif %}

{% if limit %}
LIMIT {{ limit }}
{% endif %}
