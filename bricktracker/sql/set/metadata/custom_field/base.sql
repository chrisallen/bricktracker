SELECT
    "bricktracker_metadata_custom_fields"."id",
    "bricktracker_metadata_custom_fields"."name",
    "bricktracker_metadata_custom_fields"."type"
FROM "bricktracker_metadata_custom_fields"

{% block where %}{% endblock %}

{% if order %}
ORDER BY {{ order }}
{% endif %}
