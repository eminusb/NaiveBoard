import re
from jinja2 import evalcontextfilter, Markup, escape
import sys

#_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')
_paragraph_re = re.compile(r'(?:\r\n|\r(?!\n)|\n){2,}')

@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
        for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


#_url_re = re.compile('http+[^<>\s]+')
_url_re = re.compile(r'(?:\r\n|\r(?!\n)|\n){2,}')
@evalcontextfilter
def urllink(eval_ctx, value):
	for p in _url_re.split(escape(value)):
		print(p, file=sys.stderr)


#	print(eval_ctx, file=sys.stderr)
#	print('VALUE', file=sys.stderr)
#	print(value, file=sys.stderr)	
#	urltexts = _url_re.findall(value)
#	result = escape(value)
#	result = value
#	print('RESULT', file=sys.stderr)
#	print(result, file=sys.stderr)
#	print('URLTEXTS', file=sys.stderr)
#	print(urltexts, file=sys.stderr)
#	print('\n\n', file=sys.stderr)
#	for urltext in urltexts:		
#		urlmarkup = u"<a href=\"%s\">%s</a>" % (urltext, urltext)
#		print(urltext, file=sys.stderr)
#		print(urlmarkup, file=sys.stderr)
#		result.replace(urltext, urlmarkup)
#	print('\n\n', file=sys.stderr)
#	#if eval_ctx.autoescape:
#	result = Markup(result)
#	print('RESULT', file=sys.stderr)
#	print(result, file=sys.stderr)
#	return result


