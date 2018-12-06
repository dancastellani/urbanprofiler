# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="danielcastellani"
__date__ ="$May 22, 2014 3:07:49 PM$"


def clean_non_ascii(text):
	codecs = ['utf8', 'cp1252', 'ascii', 'cp037', 'iso8859_2']
	decoded = None
	for c in codecs:
		try:
			decoded = text.decode(c, 'ignore')
		except:
			print '>>>error with codec:', c
			pass
	try:
		return decoded.encode('ascii', 'ignore')
	except:
		print '\n-----------\nERROR encoding'
		print 'type:', type(text)
		print text
		raise
	return '<<<INVALID TEXT: CLEANING ERROR>>>'


def reencode_text_if_not_ascii(text):
	if text is not None and type(text) is unicode:
		return text.encode('ascii','ignore')
	else:
		return text