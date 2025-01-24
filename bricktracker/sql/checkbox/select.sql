{% extends 'checkbox/base.sql' %}

{% block where %}
WHERE "bricktracker_set_checkboxes"."id" IS NOT DISTINCT FROM :id
{% endblock %}