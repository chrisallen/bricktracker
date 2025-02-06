SELECT
    "bricktracker_metadata_tags"."id",
    "bricktracker_metadata_tags"."name"
FROM "bricktracker_metadata_tags"

{% block where %}{% endblock %}

{% if order %}
ORDER BY {{ order }}
{% endif %}
