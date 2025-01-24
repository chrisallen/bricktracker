{% extends 'wish/base/base.sql' %}

{% block where %}
WHERE "bricktracker_wishes"."set" IS NOT DISTINCT FROM :set
{% endblock %}
