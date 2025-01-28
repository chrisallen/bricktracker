
{% extends 'part/base/base.sql' %}

{% block total_missing %}
IFNULL("bricktracker_parts"."missing", 0) AS "total_missing",
{% endblock %}

{% block where %}
WHERE "bricktracker_parts"."id" IS NOT DISTINCT FROM :id
AND "bricktracker_parts"."figure" IS NOT DISTINCT FROM :figure
{% endblock %}
