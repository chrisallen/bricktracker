{% extends 'set/base/full.sql' %}

{% block where %}
WHERE "bricktracker_sets"."storage" IS NOT DISTINCT FROM :storage
{% endblock %}
