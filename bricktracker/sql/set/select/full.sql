{% extends 'set/base/full.sql' %}

{% block where_missing %}
WHERE "missing"."u_id" IS NOT DISTINCT FROM :id
{% endblock %}

{% block where_minifigures %}
WHERE "bricktracker_minifigures"."bricktracker_set_id" IS NOT DISTINCT FROM :id
{% endblock %}

{% block where %}
WHERE "bricktracker_sets"."id" IS NOT DISTINCT FROM :id
{% endblock %}
