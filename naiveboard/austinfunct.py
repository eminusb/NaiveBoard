
def get_taglist(tags):
	taglist = []
	print(tags)
	for tag in tags.split(';'):
		tag = tag.strip()
		if tag != "":
			taglist.append(tag)	
	print(taglist)		
	return taglist

