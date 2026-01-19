SELECT
    "bricktracker_metadata_purchase_locations"."id",
    "bricktracker_metadata_purchase_locations"."name",
    {% block total_sets %}
    NULL as "total_sets" -- dummy for order: total_sets
    {% endblock %}
FROM "bricktracker_metadata_purchase_locations"

{% block join %}{% endblock %}

{% block where %}{% endblock %}

{% block group %}{% endblock %}

{% if order %}
ORDER BY {{ order }}
{% endif %}
