from django.contrib import admin

# from django.contrib.admin import AdminSite
# class MyAdminSite(AdminSite):
#     site_header = 'Finder Administration'
# admin_site = MyAdminSite(name='Finder Admin')


from finder.models import Database, Column, GpsData, Alarm, System

class ColumnInline(admin.TabularInline):
    model = Column

class GPSInline(admin.TabularInline):
    model = GpsData
    classes= ('collapse',)


class DatabaseAdmin(admin.ModelAdmin):
    # fieldsets = [
    # 				(None,               {'fields': ['database_id']}),
    # 				('Database Info', {#'classes': ('collapse',),
    #     								'fields': ['rows',
    #     											 'missing_rows', 
    #     											 'columns_count',
    #     											  'columns_geo_count',
    #     											  'columns_numeric_count', 
    #     											  'columns_temporal_count',
    #     											  'columns_text_count',
    #     											  'values',
    #     											  'values_missing']}
    #     			),
    #     			('Profiler Info', {#'classes': ('collapse',),
    #     								'fields': ['profiler_input_file',
    #     											 'profiler_status', 
    #     											 'profiler_time_begin',
    #     											  'profiler_time_end',
    #     											  'socrata_author', 
    #     											  'socrata_download_count',
    #     											  'socrata_view_count']}
    #     			),
    #     			('Socrata Metadata', {#'classes': ('collapse',),
    #     								'fields': ['socrata_status',
    #     											 'socrata_description', 
    #     											 'socrata_category',
    #     											  'socrata_owner',
    #     											  'socrata_author', 
    #     											  'socrata_download_count',
    #     											  'socrata_view_count']}
    #     			),
    #     			('GPS Data', {#'classes': ('collapse',),
    #     								'fields': [ 'gps_values', 'lat_min', 'lat_max', 'long_min', 'long_max']}
    #     			),
    # 			]

    list_display = ('database_id', 'name', 'category', 'short_profiler_status', 'socrata_status', 
                    #'socrata_primary', 'rows', 'columns_count', 'missing_percent', 
                    'source_agency',
                    'has_bounding_box')
    search_fields = ('profiler_status','database_id','category','name', 'description','owner','tags',)
    list_filter = ['profiler_status', 'category', 'owner', 'author', 'socrata_status']

    prepopulated_fields = {'name': ('database_id',)}

    inlines = [ColumnInline
                #, GPSInline
                ]
    
admin.site.register(Database, DatabaseAdmin)

class AlarmAdmin(admin.ModelAdmin):
    list_display = ['name', 'severity', 'query']
    list_filter = ['severity']

admin.site.register(Alarm, AlarmAdmin)

class SystemAdmin(admin.ModelAdmin):
    list_display = ['update_time', 'source_file']

admin.site.register(System, SystemAdmin)

