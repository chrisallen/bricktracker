{% extends 'set/base/full.sql' %}

{% block where %}
WHERE "bricktracker_sets"."purchase_location" IS NOT DISTINCT FROM :purchase_location
{% endblock %}
