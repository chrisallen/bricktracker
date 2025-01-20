SELECT
    "inventory"."set_num",
    "inventory"."id",
    "inventory"."part_num",
    "inventory"."name",
    "inventory"."part_img_url",
    "inventory"."part_img_url_id",
    "inventory"."color_id",
    "inventory"."color_name",
    "inventory"."quantity",
    "inventory"."is_spare",
    "inventory"."element_id",
    "inventory"."u_id",
    {% block total_missing %}
    NULL AS "total_missing", -- dummy for order: total_missing
    {% endblock %}
    {% block total_quantity %}
    NULL AS "total_quantity", -- dummy for order: total_quantity
    {% endblock %}
    {% block total_spare %}
    NULL AS "total_spare", -- dummy for order: total_spare
    {% endblock %}
    {% block total_sets %}
    NULL AS "total_sets", -- dummy for order: total_sets
    {% endblock %}
    {% block total_minifigures %}
    NULL AS "total_minifigures" -- dummy for order: total_minifigures
    {% endblock %}
FROM "inventory"

{% block join %}{% endblock %}

{% block where %}{% endblock %}

{% block group %}{% endblock %}

{% if order %}
ORDER BY {{ order }}
{% endif %}

{% if limit %}
LIMIT {{ limit }}
{% endif %}
