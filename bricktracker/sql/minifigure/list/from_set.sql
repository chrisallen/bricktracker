{% extends 'minifigure/base/base.sql' %}

{% block where %}
WHERE "bricktracker_minifigures"."bricktracker_set_id" IS NOT DISTINCT FROM :bricktracker_set_id
{% endblock %}
