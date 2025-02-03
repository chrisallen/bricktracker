
{% extends 'part/base/base.sql' %}

{% block total_missing %}{% endblock %}

{% block total_damaged %}{% endblock %}

{% block where %}
WHERE "bricktracker_parts"."color" IS DISTINCT FROM :color
AND "bricktracker_parts"."part" IS NOT DISTINCT FROM :part
{% endblock %}

{% block group %}
GROUP BY
    "bricktracker_parts"."part",
    "bricktracker_parts"."color"
{% endblock %}
