from django.template import Library, Node
from django_countries import countries

register = Library()

@register.simple_tag
def get_countries():
	cts = []
	for code, name in list(countries):
		cts.append({"code":code, "name":name})
	return cts
