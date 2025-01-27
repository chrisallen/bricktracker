{% extends 'minifigure/base/base.sql' %}

{% block where %}
WHERE "bricktracker_minifigures"."id" IS NOT DISTINCT FROM :id
{% endblock %}
