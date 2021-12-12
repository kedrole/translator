from django import template
register = template.Library()

import sys
sys.path.append("..") 

from main.models import Article

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

#@register.filter
#def in_list(value, list_):
#  return value in list_.split(',')

@register.filter
def in_list(var, obj):
    return var in obj

@register.filter
def get_stage_status(article, stage):
    stages_list = [stage for (stage, descr) in Article._meta.get_field('stage').choices]

    if article.stage not in stages_list:
        return ""
        
    if stages_list.index(article.stage) > stages_list.index(stage):
        return "done"
    elif stages_list.index(article.stage) == stages_list.index(stage):
        return "active"
    else:
        return ""