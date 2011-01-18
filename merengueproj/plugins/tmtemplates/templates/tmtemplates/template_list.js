var tinyMCETemplateList = [
{% for template in templates %}
	['{{ template.name }}', '{% url tmtemplate_view template.id %}', '{{ template.description }}']{% if not forloop.last %},{% endif %}
{% endfor %}
];
