import re
from jinja2 import evalcontextfilter, Markup, escape
import sys

#_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')
'''
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
        for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result
'''
_paragraph_re = re.compile(r'(?:\r\n|\r(?!\n)|\n){2,}')
@evalcontextfilter
def nl2br(eval_ctx, value):
	result = ""
	for p in _paragraph_re.split(escape(value)):
		newp = p.replace('\n', '<br>\n')
		newp = '<p>'+newp+'</p>'
		result += newp

	if eval_ctx.autoescape:
		result = Markup(result)
	return result



_url_re = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
@evalcontextfilter
def urllink(eval_ctx, value):
	result = "" 
	urllist = _url_re.findall(escape(value))
	parlist = _url_re.split(escape(value))
	i = 0
	while i < len(urllist):
		urlmarkup = '<a href=\"%s\" target=\"_blank\">%s</a>' % (urllist[i], urllist[i])
		result += parlist[i] + urlmarkup
		i = i+1
	result += parlist[i]

	if eval_ctx.autoescape:
		result = Markup(result)
	return result
