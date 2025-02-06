{% extends 'set/metadata/purchase_location/base.sql' %}

{% block where %}
WHERE "bricktracker_metadata_purchase_locations"."id" IS NOT DISTINCT FROM :id
{% endblock %}