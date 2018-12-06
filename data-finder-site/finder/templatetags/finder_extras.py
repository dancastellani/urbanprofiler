from random import randint
from django import template
import re
import os

register = template.Library()

# @register.simple_tag(takes_context=True)
# def with_current_query(context, kwargs):

@register.filter(name='is_current_env')
def is_current_env(needed_env):
    return needed_env and needed_env == os.environ.get('URBAN_PROFILER_ENVORINMENT')

    
@register.simple_tag(takes_context=True)
def url_add_query(context, **kwargs):
    request = context.get('request')

    get = request.GET.copy()
    get.update(kwargs)

    path = '%s?' % request.path
    for query, val in get.items():
        path += '%s=%s&' % (query, val)

    return path[:-1]

##ref: http://www.vermontdatabase.com/cloudwriter/url_encoding.htm
##ref: http://www.w3schools.com/tags/ref_urlencode.asp
@register.filter(name='escape_url')
def escape_url(arg):
    if arg is None: return arg
    return_str = arg.replace('&', '%26')
    return_str = return_str.replace('(', '%28')
    return_str = return_str.replace(')', '%29')
    return_str = return_str.replace('#', '%23')
    return_str = return_str.replace(' ', '%20')
    return_str = return_str.replace('\n', '%0A')
    # return_str = return_str.replace('$', '%24')
    return return_str

@register.filter(name='until_breakline')
def until_breakline(arg):
    if arg is None: return arg

    return arg.split('\n')[0]
    
@register.filter(name='escape_for_js')
def escape_for_js(arg):
    print '-------------------__>', arg
    if arg is None: return arg
    return_str = arg.replace('\n', '')
    print '------------------- 2>', arg
    return return_str

@register.simple_tag()
def random_number():
    length=3
    return randint(10**(length-1), (10**(length)-1))

@register.filter(name='slice_in_sizes_of')
def slice_in_sizes_of(value, size):
    return [value[i:i+size] for i in range(0, len(value), size)]

@register.filter(name='percent_of')
def percent_of(portion, total):
    return portion*100/total

@register.simple_tag(takes_context=True)
def call_with_args(context, object_name, method, args):
    return eval( 'context.get("{0}").{1}("{2}")'.format(object_name, method, args) )

@register.filter(name='concat')
def concat(this, other):
    return '{0}{1}'.format(this, other)

import re
@register.filter(name='eval')
def eval_str(string):
    if string.lower() == 'none':
        return ''
    print '=====>', string

    REGEX_NULL = re.compile(r"\bnull\b", re.IGNORECASE)
    # replace the null valor for "null" string
    # remove the first and last " that the regex adds
    string = re.sub(REGEX_NULL, '\'Null\'', string)[1:-1]
    if len(string) == 0: return None
    return eval(string)