{% extends 'set/metadata/storage/base.sql' %}

{% block where %}
WHERE "bricktracker_metadata_storages"."id" IS NOT DISTINCT FROM :id
{% endblock %}