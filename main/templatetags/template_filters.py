#from django.template.defaulttags import register

from django import template
register = template.Library()

@register.filter
def css_color_style_from_degree(val):
    R = 0
    G = 0
    B = 0
    if 0 <= val < 66.6:
        R = 100
        G = int(val * 1.5)
    elif 66.6 <= val <= 100:
        R = 0
        G = 80 + (100 - val) * 0.6
    else:
        R = 255
        G = 255
        B = 255

    return "rgb(" + str(R) + "," + str(G) + "," + str(B) + ");"
