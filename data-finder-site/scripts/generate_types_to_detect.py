from profiler.models import SimpleType, DetailedType

def run(*args):
	print 'Received args=', args
	if len(args) != 1 or not args[0] or args[0] == '': 
		raise Exception('[ERROR] Output file must be passed as param. Only this param should be used.')


	output_csv = ''

	for stype in SimpleType.objects.extra(order_by = ['global_order']).all():
		
		for dtype in stype.detailedtype_set.extra(order_by = ['order_in_type']).all():
			output_csv += stype.name + ', ' 
			output_csv += dtype.name + ', '
			if dtype.values_regex: 
				output_csv += '"{0}", '.format(dtype.values_regex)
			else: 
				output_csv += ','
			if dtype.values_dictionary: 
				output_csv += '"{0}", '.format(dtype.values_dictionary.replace('"', '\\"'))
			else: 
				output_csv += ','
			output_csv += '{0}, {1}'.format(dtype.dictionary_is_file, dtype.accept_missing_values)
			output_csv += ', "{0}"'.format(dtype.dictionary_type)
			output_csv += '\n'
	print 'CSV:', output_csv

	with open(args[0], "w") as text_file:
		text_file.write(output_csv)

	print 'File ', args[0], ' saved.'
