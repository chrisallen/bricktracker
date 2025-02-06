{% extends 'set/metadata/tag/base.sql' %}

{% block where %}
WHERE "bricktracker_metadata_tags"."id" IS NOT DISTINCT FROM :id
{% endblock %}