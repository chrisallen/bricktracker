{% extends 'minifigure/base/base.sql' %}

{% block where %}
WHERE "rebrickable_minifigures"."figure" IS NOT DISTINCT FROM :figure
AND "bricktracker_minifigures"."id" IS NOT DISTINCT FROM :id
{% endblock %}
