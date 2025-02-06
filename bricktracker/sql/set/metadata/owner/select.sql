{% extends 'set/metadata/owner/base.sql' %}

{% block where %}
WHERE "bricktracker_metadata_owners"."id" IS NOT DISTINCT FROM :id
{% endblock %}