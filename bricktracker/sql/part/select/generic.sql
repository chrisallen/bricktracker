{% extends 'part/base/base.sql' %}

{% block total_missing %}
SUM("bricktracker_parts"."missing") AS "total_missing",
{% endblock %}

{% block total_damaged %}
SUM("bricktracker_parts"."damaged") AS "total_damaged",
{% endblock %}

{% block total_quantity %}
SUM((NOT "bricktracker_parts"."spare") * "bricktracker_parts"."quantity" * IFNULL("bricktracker_minifigures"."quantity", 1)) AS "total_quantity",
{% endblock %}

{% block total_spare %}
SUM("bricktracker_parts"."spare" * "bricktracker_parts"."quantity" * IFNULL("bricktracker_minifigures"."quantity", 1)) AS "total_spare",
{% endblock %}

{% block join %}
LEFT JOIN "bricktracker_minifigures"
ON "bricktracker_parts"."id" IS NOT DISTINCT FROM "bricktracker_minifigures"."id"
AND "bricktracker_parts"."figure" IS NOT DISTINCT FROM "bricktracker_minifigures"."figure"
{% endblock %}

{% block where %}
WHERE "bricktracker_parts"."part" IS NOT DISTINCT FROM :part
AND "bricktracker_parts"."color" IS NOT DISTINCT FROM :color
{% endblock %}

{% block group %}
GROUP BY
    "bricktracker_parts"."part",
    "bricktracker_parts"."color"
{% endblock %}
