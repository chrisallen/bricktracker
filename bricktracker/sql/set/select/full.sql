{% extends 'set/base/full.sql' %}

{% block where_missing %}
WHERE "bricktracker_parts"."id" IS NOT DISTINCT FROM :id
{% endblock %}

{% block where_minifigures %}
WHERE "bricktracker_minifigures"."id" IS NOT DISTINCT FROM :id
{% endblock %}

{% block where %}
WHERE "bricktracker_sets"."id" IS NOT DISTINCT FROM :id
{% endblock %}
