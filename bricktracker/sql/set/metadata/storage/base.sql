SELECT
    "bricktracker_metadata_storages"."id",
    "bricktracker_metadata_storages"."name",
    {% block total_sets %}
    NULL as "total_sets" -- dummy for order: total_sets
    {% endblock %}
FROM "bricktracker_metadata_storages"

{% block join %}{% endblock %}

{% block where %}{% endblock %}

{% block group %}{% endblock %}

{% if order %}
ORDER BY {{ order }}
{% endif %}
