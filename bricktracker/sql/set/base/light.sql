SELECT
    "bricktracker_sets"."id",
    "bricktracker_sets"."set"
FROM "bricktracker_sets"

{% block join %}{% endblock %}

{% block where %}{% endblock %}

{% block group %}{% endblock %}

{% if order %}
ORDER BY {{ order }}
{% endif %}

{% if limit %}
LIMIT {{ limit }}
{% endif %}
