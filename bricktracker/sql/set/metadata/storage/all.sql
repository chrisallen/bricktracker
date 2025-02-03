{% extends 'set/metadata/storage/base.sql' %}

{% block total_sets %}
IFNULL(COUNT("bricktracker_sets"."id"), 0) AS "total_sets"
{% endblock %}

{% block join %}
LEFT JOIN "bricktracker_sets"
ON "bricktracker_metadata_storages"."id" IS NOT DISTINCT FROM "bricktracker_sets"."storage"
{% endblock %}

{% block group %}
GROUP BY "bricktracker_metadata_storages"."id"
{% endblock %}