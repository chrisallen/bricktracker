{% extends 'minifigure/base/base.sql' %}

{% block where %}
WHERE "bricktracker_minifigures"."id" IS NOT DISTINCT FROM :id
AND "rebrickable_minifigures"."figure" IS NOT DISTINCT FROM :figure
{% endblock %}
