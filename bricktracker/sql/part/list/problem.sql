{% extends 'part/base/base.sql' %}

{% block total_missing %}
SUM("bricktracker_parts"."missing") AS "total_missing",
{% endblock %}

{% block total_damaged %}
SUM("bricktracker_parts"."damaged") AS "total_damaged",
{% endblock %}

{% block total_sets %}
IFNULL(COUNT("bricktracker_parts"."id"), 0)  - IFNULL(COUNT("bricktracker_parts"."figure"), 0) AS "total_sets",
{% endblock %}

{% block total_minifigures %}
SUM(IFNULL("bricktracker_minifigures"."quantity", 0)) AS "total_minifigures"
{% endblock %}

{% block join %}
LEFT JOIN "bricktracker_minifigures"
ON "bricktracker_parts"."id" IS NOT DISTINCT FROM "bricktracker_minifigures"."id"
AND "bricktracker_parts"."figure" IS NOT DISTINCT FROM "bricktracker_minifigures"."figure"
{% endblock %}

{% block where %}
WHERE "bricktracker_parts"."missing" > 0
OR "bricktracker_parts"."damaged" > 0
{% endblock %}

{% block group %}
GROUP BY
    "bricktracker_parts"."part",
    "bricktracker_parts"."color",
    "bricktracker_parts"."spare"
{% endblock %}
