
def parse_taginput(taginput):

	taglist = list()	
	for tag in taginput.split(';'):
		tag = tag.strip()
		if tag != "" and (not tag in taglist):
			taglist.append(tag)	

	return taglist


if __name__=='__main__':
	tags = "123;abc; ABC; def; hij; abc; DEF"
	tagtextlist = parse_taginput(tags)
	print(tagtextlist)
	print("; ".join(tagtextlist))
