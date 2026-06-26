{% extends 'set/metadata/custom_field/base.sql' %}

{% block where %}
WHERE "bricktracker_metadata_custom_fields"."id" IS NOT DISTINCT FROM :id
{% endblock %}
