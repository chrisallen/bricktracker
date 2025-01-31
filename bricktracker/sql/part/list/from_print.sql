
{% extends 'part/base/base.sql' %}

{% block total_missing %}{% endblock %}

{% block total_damaged %}{% endblock %}

{% block where %}
WHERE "rebrickable_parts"."print" IS NOT DISTINCT FROM :print
AND "bricktracker_parts"."color" IS NOT DISTINCT FROM :color
AND "bricktracker_parts"."part" IS DISTINCT FROM :part
{% endblock %}

{% block group %}
GROUP BY
    "bricktracker_parts"."part",
    "bricktracker_parts"."color"
{% endblock %}
