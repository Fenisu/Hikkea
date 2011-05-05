# -*- coding: utf-8 -*-

from django import template
import re
register = template.Library()

@register.filter(name='debug')
def debug(value):
    print(value)
    print(type(value))
    print(dir(value))

@register.filter(name='items')
def items(value):
    to_del = ('npackage', value['npackage'])
    items = value.items()
    items.remove(to_del)
    return items
    
@register.filter(name='namepackage')
def namepackage(value):
    # Se quita el partX
    return re.sub('\.part\d+$|\.\d+$', '', value)

@register.filter(name='ifnull')
def ifnull(value, default):
    print(value)
    print(default)
    if value:
        return value
    else:
        return default


#@register.filter(name='radio')
#def radio(value):
    #options = []
    #print(dir(value))
    #for key, value in value.field.widget.choices:
        #pass
        #'<label for="id_%(name)s">'\
            #'<input type="radio" name="my_field"'\
                   #'value="abc" id="id_my_field_x" />'\
        #</label>'