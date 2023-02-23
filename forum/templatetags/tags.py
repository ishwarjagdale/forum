import random

from django import template


def get_first_name(name):
    return name.split()[0]


def random_color():
    return f"rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})"


def singular(a):
    return a > 1


def shorten_natural_time(string):
    return str(string[:-len('ago')].split(",")[0]).strip() + " ago"


register = template.Library()
register.filter('get_first_name', get_first_name)
register.simple_tag(random_color, name='random_color')
register.filter('singular', singular)
register.filter('shorten_natural_time', shorten_natural_time)
