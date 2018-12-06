from django.contrib import admin

# Register your models here.
from profiler.models import DetailedType, SimpleType

class DetailedTypeInline(admin.TabularInline):
    model = DetailedType
    classes= ('collapse',)


class SimpleTypeAdmin(admin.ModelAdmin):

    list_display = ('name', 'global_order_presentation', 'global_order', 'related_detailed_types')
    # search_fields = ('database_id',)
    # list_filter = ['category', 'socrata_primary', 'owner', 'author', 'socrata_status']

    # prepopulated_fields = {'name': ('database_id',)}

    inlines = [DetailedTypeInline, ]
    
admin.site.register(SimpleType, SimpleTypeAdmin,)