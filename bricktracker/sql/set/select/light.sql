{% extends 'set/base/light.sql' %}

{% block where %}
WHERE "bricktracker_sets"."id" IS NOT DISTINCT FROM :id
{% endblock %}
