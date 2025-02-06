SELECT
    "bricktracker_metadata_statuses"."id",
    "bricktracker_metadata_statuses"."name",
    "bricktracker_metadata_statuses"."displayed_on_grid"
FROM "bricktracker_metadata_statuses"

{% block where %}{% endblock %}

{% if order %}
ORDER BY {{ order }}
{% endif %}
