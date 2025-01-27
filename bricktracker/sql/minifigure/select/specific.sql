{% extends 'minifigure/base/base.sql' %}

{% block where %}
WHERE "rebrickable_minifigures"."figure" IS NOT DISTINCT FROM :figure
AND "bricktracker_minifigures"."bricktracker_set_id" IS NOT DISTINCT FROM :bricktracker_set_id
{% endblock %}
