from django.db import models

# Create your models here.
class SimpleType(models.Model):
	name = models.CharField(max_length=256, blank=True, null=True, default=None, unique=True)
	global_order = models.IntegerField(blank=False, null=False, help_text="Use an integer positive value 1-based to indicate the order. Ascendent order will be considered.")
	global_order_presentation = models.IntegerField(blank=False, null=False, help_text="Use an integer positive value 1-based to indicate the order. Ascendent order will be considered.")

	color = models.CharField(max_length=20, blank=False, null=False, default='#FFF')


	def __str__(self):
		return str(self.global_order) + '. ' + self.name + ' (' + self.related_detailed_types() + ')'

	def related_detailed_types(self):
		detailed_types = ''
		for dt in self.detailedtype_set.extra(order_by = ['order_in_type']).all():
			detailed_types += dt.name + ', '
		return detailed_types.strip(', ')

	class Meta:
	 	ordering = ['global_order', 'name']

class DetailedType(models.Model):
	simple_type = models.ForeignKey(SimpleType)
	name = models.CharField(max_length=256, blank=True, null=True, default=None, unique=True)
	
	order_in_type = models.IntegerField(blank=False, null=False, help_text="Use an integer positive value 1-based to indicate the order. Ascendent order will be considered.")
	order_in_type_presentation = models.IntegerField(blank=False, null=False, help_text="Use an integer positive value 1-based to indicate the order. Ascendent order will be considered.")
	
	values_regex = models.CharField(max_length=256, blank=True, null=True)
	values_dictionary = models.CharField(max_length=256, blank=True, null=True, help_text="in CSV format. Use double quotes for values with space.")

	color = models.CharField(max_length=20, blank=False, null=False, default='#FFF')

	EQUAL = 'Equal'
	CONTAINS = 'Contains'
	CONTAINS_WORD = 'Contains Word'
	DICTIONARY_TYPE_CHOICES = (
		(EQUAL, EQUAL), 
		(CONTAINS, CONTAINS),
		(CONTAINS_WORD, CONTAINS_WORD)
	)
	dictionary_type	= models.CharField(max_length=20, choices=DICTIONARY_TYPE_CHOICES, default=EQUAL)
	

	dictionary_is_file = models.BooleanField(default=False, help_text="Check this if the dictionary is on a file on 'resources' folder.")
	accept_missing_values = models.BooleanField(default=False, help_text="Check this if the missing values should be counted on this type.")

	def full_name(self):
		if self.name == self.simple_type.name: return self.name
		else: return self.simple_type.name + '-' + self.name

	def __str__(self):
		return self.name

	class Meta:
	 	ordering = ['order_in_type', 'name']
