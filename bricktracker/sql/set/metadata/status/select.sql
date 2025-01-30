{% extends 'set/metadata/status/base.sql' %}

{% block where %}
WHERE "bricktracker_metadata_statuses"."id" IS NOT DISTINCT FROM :id
{% endblock %}