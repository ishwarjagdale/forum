import random

import markdown
from django import template


def to_html(value):
    return markdown.markdown(value, extensions=['fenced_code'])


def get_first_name(name):
    return name.split()[0]


def random_color():
    return f"rgb({random.randint(50, 255)}, {random.randint(50, 255)}, {random.randint(50, 255)})"


def random_int(arg=None):
    return list(range(random.randint(1, 5)))


def singular(a):
    return a > 1


def shorten_natural_time(string):
    return str(string[:-len('ago')].split(",")[0]).strip() + " ago"


def to_tags(tags):
    return set(filter(lambda x: len(x) > 0, map(lambda x: x.strip(), tags.split('\n'))))


register = template.Library()
register.filter('get_first_name', get_first_name)
register.simple_tag(random_color, name='random_color')
register.filter('to_html', to_html)
register.filter('to_tags', to_tags)
register.filter('random_int', random_int)
register.filter('singular', singular)
register.filter('shorten_natural_time', shorten_natural_time)
