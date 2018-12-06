class Dataset:
	def __init__(self, resources = [], title = None, description = None, provided_metadata = None):
		self.resources = resources
		self.title = title
		self.description = description

		#Provided Metadata
		self.provided_metadata = provided_metadata

	def __str__(self):
		if title and description:
			return "{}:{}".format(title, description)
		else:
			return ''

class Resource:
	def __init__(self, dataset, title = None):
		self.dataset = dataset

		self.title = title

		self.rows = None
		self.columns = None