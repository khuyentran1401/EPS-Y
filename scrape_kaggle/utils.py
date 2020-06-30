import os




def string2dic(string):
	dic = {}
	dics = []
	pal_actual = 'dic'
	dic_actual = dic
	list_ = False
	for j in string.split('''"'''):
		for k in j.split("'"):
			for i in k.split(','):
				if i == '{':
					dics.append(dic_actual)
					dic_actual[pal_actual] = {}
					dic_actual = dic_actual[pal_actual]
					continue

				if "}" in i:
					dic_actual[pal_actual] = i
					try:
						if list_:
							dics[-1].append(dic_actual)
						dic_actual = dics.pop()
					except:
						break
					continue

				if ":" in i:
					dic_actual[pal_actual] = i[1:]
					continue

				if "[" in i:
					list_ = True
				if "]" in i:
					list_  = False

				pal_actual = i

	return dic