SELECT
    "bricktracker_metadata_purchase_locations"."id",
    "bricktracker_metadata_purchase_locations"."name"
FROM "bricktracker_metadata_purchase_locations"

{% block where %}{% endblock %}

{% if order %}
ORDER BY {{ order }}
{% endif %}
