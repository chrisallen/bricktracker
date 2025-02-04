SELECT
    "bricktracker_metadata_owners"."id",
    "bricktracker_metadata_owners"."name"
FROM "bricktracker_metadata_owners"

{% block where %}{% endblock %}

{% if order %}
ORDER BY {{ order }}
{% endif %}
