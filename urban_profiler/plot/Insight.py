# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="danielcastellani"
__date__ ="$May 22, 2014 4:32:17 PM$"

#Plot all summaries to one folder
# --verbose  --to_folder=/tmp/profilers --summaries=/home/danielcastellani/Documents/databases/etl-profilers/p21_2014-10-28/_etl-profiler-summary-2014-10-28_22-41-04.csv

from utils import CLI 
from utils import PandasUtils 
from profiler import TypeDetector
from matplotlib import pyplot as plt
from utils import FileUtils
from utils import ProfilerUtils
from utils import MapUtils
from os import path
import pandas
import numpy

v_opts = {
    'profiler': None,
    'summaries': None,
    'to_folder': None
}
b_opts = {
    'verbose': False,
    'no_basename': False
}

opts = {}


def generate_type_comparisson_with_metadata():
    summaries_file = opts['summaries']
    types_summary_file = summaries_file.replace('.csv', '_types.csv')
    if path.isfile(types_summary_file):
        print '=>', types_summary_file
        types_df = pandas.read_csv(types_summary_file)
        
        base_name = files_base_name()
        
        title = 'Socrata type -> Detected Type'
        plot_data = pandas.DataFrame()
        plot_data['Types'] = types_df['socrata-type'] + ' -> ' + types_df['profiler-type']
        plot_data['Count'] = types_df['column-name']
        plot_data = plot_data.groupby('Types').count()
        plot_to_file(plot_data, 'barh', title, base_name + title.replace(' ', '_') + '.png')
        
        title += ' (%)'
        plot_data = plot_data / plot_data.sum() * 100
        plot_to_file(plot_data, 'barh', title, base_name + title.replace(' ', '_') + '.png')
        
        title = 'Socrata type -> Profiler Most Detected Type'
        plot_data = pandas.DataFrame()
        plot_data['Types'] = types_df['socrata-type'] + ' -> ' + types_df['profiler-most-detected']
        plot_data['Count'] = types_df['column-name']
        plot_data = plot_data.groupby('Types').count()
        plot_to_file(plot_data, 'barh', title, base_name + title.replace(' ', '_') + '.png')
        
        title += ' (%)'
        plot_data = plot_data / plot_data.sum() * 100
        plot_to_file(plot_data, 'barh', title, base_name + title.replace(' ', '_') + '.png')
        
        title = 'Socrata types '
        plot_data = pandas.DataFrame()
        plot_data['Number of Columns'] = types_df['socrata-type'].value_counts().reindex(sorted(types_df['socrata-type'].unique()))
        plot_to_file(plot_data, 'bar', title, base_name + title.replace(' ', '_') + '.png')
        
        title = 'Profiler types '
        plot_data = pandas.DataFrame()
        plot_data['Number of Columns'] = types_df['profiler-type'].value_counts().reindex(sorted(types_df['profiler-type'].unique()))
        plot_to_file(plot_data, 'bar', title, base_name + title.replace(' ', '_') + '.png')
        
    else:
        print 'Types file not found.'
        
def files_base_name():
    sumaries_file = opts['summaries']
    to_folder = opts['to_folder']
    use_basename = not opts['no_basename']

    if to_folder is not None: 
        base_name = to_folder 
        if not base_name.endswith('/'): base_name += '/'
    else:
        base_name = ''
    if use_basename: base_name += FileUtils.get_file_name(sumaries_file).strip('.json').strip('.csv') + '_plot_'
    
    print 'Plots file base name: ', base_name
    return base_name

def insight_on_sumaries():
    base_name = files_base_name() + '_'
    sumaries_file = opts['summaries']
    
    sumaries = PandasUtils.load_database(sumaries_file)
    print '----------------------------------------'
    print 'Columns in summary:'
    for col in sumaries.columns: print '    ' + col
    print '----------------------------------------'
    
    SHRINK_LIMIT = 25
    title = 'ETL-Profiler Status with Skiped'
    plot_data = PandasUtils.shrink(sumaries['ETL-Profiler Status'].dropna(), SHRINK_LIMIT)
    plot_data = plot_data.value_counts().reindex(sorted(plot_data.unique()))
    plot_to_file(plot_data, 'barh', title, base_name + title.replace(' ', '_') + '.png')
    
    #Remove skipped datasets
    status_col = sumaries['ETL-Profiler Status']
    sumaries = sumaries[status_col.apply(lambda x: 'SKIP' not in x)]
    
    title = 'ETL-Profiler Status'
    plot_data = PandasUtils.shrink(sumaries['ETL-Profiler Status'].dropna(), SHRINK_LIMIT)
    plot_data = plot_data.value_counts().reindex(sorted(plot_data.unique()))
    plot_to_file(plot_data, 'barh', title, base_name + title.replace(' ', '_') + '.png')
    
    title = 'ETL-Profiler Status Errors Only'
    plot_data = sumaries['ETL-Profiler Status'][sumaries['ETL-Profiler Status'].apply(lambda x: 'Error' in x)].dropna()
    plot_data = PandasUtils.shrink(plot_data, SHRINK_LIMIT)
    plot_data = plot_data.value_counts().reindex(sorted(plot_data.unique()))
    plot_to_file(plot_data, 'barh', title, base_name + title.replace(' ', '_') + '.png', colormap=COLOR_RED_TO_BLUE)
    
    title = 'Number of Column Types by Number of Databases'
    colors, types = simple_colors_and_types()
    types = types[:-1]
    plot_data = pandas.DataFrame({'Numeric': sumaries.groupby('Columns Numeric').count().icol(0),
                                    'Geo': sumaries.groupby('Columns Geo').count().icol(0),
                                    'Temporal': sumaries.groupby('Columns Temporal').count().icol(0),
                                    'Textual': sumaries.groupby('Columns Text').count().icol(0)})
    plot_data = plot_data[types]
    plot_to_file(plot_data, 'bar', title, base_name + title.replace(' ', '_') + '.png')
#   
    count_ok = (sumaries['ETL-Profiler Status'] == 'OK').value_counts()[True]
    title = 'Databases per Detected Type (Considered: {0})'.format(count_ok)
    plot_data = pandas.DataFrame({'Numeric': (sumaries['Columns Numeric'] > 0).value_counts()[True],
                                    'Geo': (sumaries['Columns Geo'] > 0).value_counts()[True],
                                    'Temporal': (sumaries['Columns Temporal'] > 0).value_counts()[True],
                                    'Textual': (sumaries['Columns Text'] > 0).value_counts()[True]}, index=['Total'])
    plot_data = plot_data[types]
    plot_to_file(plot_data, 'bar', title, base_name + title.replace(' ', '_') + '.png', colors=colors)

    title = 'Databases per Detected Type (Considered: {0}) (%)'.format(count_ok)
    plot_data = (plot_data.T * 100.0 / plot_data.T.sum()).T
    plot_to_file(plot_data, 'bar', title, base_name + title.replace(' ', '_') + '.png', colors=colors)

#   
    title = 'Number of Columns per Detected Type'
    plot_data = pandas.DataFrame({'Numeric': sumaries['Columns Numeric'].sum(),
                                    'Geo': sumaries['Columns Geo'].sum(),
                                    'Temporal': sumaries['Columns Temporal'].sum(),
                                    'Textual': sumaries['Columns Text'].sum()}, index=['Total'])
    plot_data = plot_data[types]
    plot_to_file(plot_data, 'bar', title, base_name + title.replace(' ', '_') + '.png', colors=colors)
    
    title = 'Number of Columns per Detected Type (%)'
    plot_data = (plot_data.T * 100.0 / plot_data.T.sum()).T
    plot_to_file(plot_data, 'bar', title, base_name + title.replace(' ', '_') + '.png', colors=colors)

    title = 'Detected Data Type (Rows - Complete)'
    temp = sumaries['Types Percent Complete'].dropna().apply(lambda x: ProfilerUtils.get_types_data_as_DataFrame_with_NULL_last(x))
    plot_data = pandas.DataFrame(index=temp.keys())
    colors, types = simple_colors_and_types_complete()
    for type in types:
        plot_data[type] = temp.apply(lambda x: x[type].sum() if type in x.columns else 0)
    plot_data = plot_data.sum()
    plot_to_file(plot_data, 'bar', title, base_name + title.replace(' ', '_') + '.png', colors=colors)
    
    title = 'Detected Data Type (Rows - Complete) (%)'
    plot_data = plot_data * 100.0 / plot_data.sum()
    plot_to_file(plot_data, 'bar', title, base_name + title.replace(' ', '_') + '.png', colors=colors)
    
    title = 'Histogram of Values Missing Percent'
    plot_data = sumaries['Values Missing Percent']
    plot_to_file(plot_data, 'histogram', title, base_name + title.replace(' ', '_') + '.png', bins=30)
    
    title = 'Histogram of Socrata Comments Count'
    plot_data = sumaries['Socrata Comments']
    plot_to_file(plot_data, 'histogram', title, base_name + title.replace(' ', '_') + '.png', bins=50)

    title = 'Histogram of Socrata Downloads'
    plot_data = sumaries['Socrata Download Count']
    plot_to_file(plot_data, 'histogram', title, base_name + title.replace(' ', '_') + '.png', bins=50)

    title = 'Histogram of Socrata Views'
    plot_data = sumaries['Socrata View Count']
    plot_to_file(plot_data, 'histogram', title, base_name + title.replace(' ', '_') + '.png', bins=50)
    
    title = 'Databases by Socrata Access Status'
    plot_data = sumaries['Socrata_Status'].dropna().value_counts()
    plot_to_file(plot_data, 'barh', title, base_name + title.replace(' ', '_') + '.png')
    
    title = 'Databases by Socrata Author'
    plot_data = sumaries['Socrata Author'].dropna().value_counts()
    plot_to_file(plot_data, 'barh', title, base_name + title.replace(' ', '_') + '.png')
    
    title = 'Databases by Socrata Owner'
    plot_data = sumaries['Socrata Owner'].dropna().value_counts()
    plot_to_file(plot_data, 'barh', title, base_name + title.replace(' ', '_') + '.png')
    
    title = 'Databases by Socrata Category'
    plot_data = sumaries['Socrata Category'].dropna().value_counts()
    plot_to_file(plot_data, 'barh', title, base_name + title.replace(' ', '_') + '.png')
    
    title = 'Rows by Socrata Category'
    plot_data = sumaries[['Socrata Category', 'Rows']].groupby('Socrata Category').sum()
    plot_to_file(plot_data, 'bar', title, base_name + title.replace(' ', '_') + '.png')
    
    #====================================================================================================
    base_name = base_name.replace('__', '_')
    
    title = 'Histogram of Number of Columns'
    plot_data = sumaries['Columns']
    plot_to_file(plot_data, 'histogram', title, base_name + title.replace(' ', '_') + '.png')
    
    title = 'Histogram of Geo Columns'
    plot_data = sumaries['Columns Geo']
    plot_to_file(plot_data, 'histogram', title, base_name + title.replace(' ', '_') + '.png')
    
    title = 'Histogram of Text Columns'
    plot_data = sumaries['Columns Text']
    plot_to_file(plot_data, 'histogram', title, base_name + title.replace(' ', '_') + '.png')
    
    title = 'Histogram of Numeric Columns'
    plot_data = sumaries['Columns Numeric']
    plot_to_file(plot_data, 'histogram', title, base_name + title.replace(' ', '_') + '.png')
    
    title = 'Histogram of Rows'
    plot_data = sumaries['Rows']
    plot_to_file(plot_data, 'histogram', title, base_name + title.replace(' ', '_') + '.png', bins=50)
    
    title = 'Histogram of Input File Size (KB)'
    plot_data = sumaries['ETL-Profiler Input File Size (KB)']
    plot_to_file(plot_data, 'histogram', title, base_name + title.replace(' ', '_') + '.png', bins=50)
    
    title = 'Histogram of Processing Time (sec)'
    plot_data = sumaries['ETL-Profiler Processing Time (sec)']
    plot_to_file(plot_data, 'histogram', title, base_name + title.replace(' ', '_') + '.png', bins=50)
    
    title = 'Histogram of Total Memory (MB)'
    plot_data = sumaries['ETL-Profiler Total Memory (MB)']
    plot_to_file(plot_data, 'histogram', title, base_name + title.replace(' ', '_') + '.png', bins=50)
    
    title = 'Total Memory (MB) x Rows'
    plot_data = sumaries[['Rows', 'ETL-Profiler Total Memory (MB)']].groupby('Rows').agg(numpy.average)
    plot_to_file(plot_data, 'line', title, base_name + title.replace(' ', '_') + '.png')
    
    title = 'Processing Time (sec) x Rows'
    plot_data = sumaries[['Rows', 'ETL-Profiler Processing Time (sec)']].groupby('Rows').agg(numpy.average)
    plot_to_file(plot_data, 'line', title, base_name + title.replace(' ', '_') + '.png')
    
    title = 'Rows by Number of Columns'
    plot_data = sumaries[['Columns', 'Rows']].groupby('Columns').sum()
    plot_to_file(plot_data, 'bar', title, base_name + title.replace(' ', '_') + '.png')
    
    title = 'Values by Number of Columns'
    plot_data = sumaries[['Columns', 'Values']].groupby('Columns').sum()
    plot_to_file(plot_data, 'bar', title, base_name + title.replace(' ', '_') + '.png')
    

    if True: return
    #===========================================================================
    
    sumaries_columns = list(sumaries.columns)
    sumaries_columns.remove('Database')
    for column_name in sumaries_columns:
        type = TypeDetector.type_of_column_data(sumaries[column_name])
        puts('Column: {0} - {1}'.format(column_name, type))

        if type is TypeDetector.NUMERIC:
            sorted_unique = sorted(data.dropna().unique())
            plot_data = data.value_counts().reindex(index=sorted_unique)
            file_name = base_name + 'column_' + column_name.replace(' ', '_')

#            puts('  Data type: {0}'.format(data.dtype))
#            puts('  Unique Values: {0:,}'.format(data.nunique()))
            if data.nunique() < 100 : 
                chart_kind = 'bar'
            else:
                chart_kind = 'line'

            plot_to_file(plot_data, chart_kind, 'Count of ' + column_name, file_name + '_' + chart_kind)
            chart_kind = 'histogram'
            plot_to_file(plot_data, chart_kind, 'Histogram of ' + column_name, file_name + '_' + chart_kind)

        else:
            # Check if is all diferent.
            # If so, nothing to do.
            if plot_data.nunique() == plot_data.count():
                puts('  All values are different. Nothing to plot.') 
                return

            sorted_unique = sorted(data.dropna().unique())

            plot_data = data.value_counts().reindex(index=sorted_unique)
            file_name = base_name + 'column_' + column_name.replace(' ', '_')

            puts('  Data type: {0}'.format(data.dtype))
            puts('  Unique Values: {0:,}'.format(data.nunique()))
            if data.nunique() < 100 : 
                chart_kind = 'barh'
                plot_to_file(plot_data, chart_kind, 'Count of ' + column_name, file_name + '_' + chart_kind)
            else:
                puts('  Too many unique values to generate chart: {0:,}'.format(data.nunique()))

def simple_colors_and_types():
    types = [TypeDetector.GEO, TypeDetector.TEMPORAL, TypeDetector.NUMERIC, TypeDetector.TEXTUAL, TypeDetector.NULL]
    colors =  ['#006d2c'     , '#08519c'            , '#fed976'           , '#ef3b2c'           , '#ffffff']
    return colors, types

def simple_colors_and_types_complete():
    types = []
    colors =  []
    
    # Colors: http://colorbrewer2.org/
    types.append(TypeDetector.GEO_GPS); colors.append('#006d2c')
    types.append(TypeDetector.GEO_ZIP); colors.append('#41ae76')
    types.append(TypeDetector.GEO_BOROUGH); colors.append('#c7e9c0')
    
    types.append(TypeDetector.TEMPORAL_DATE); colors.append('#9ecae1')
    types.append(TypeDetector.TEMPORAL_TIME); colors.append('#4292c6')
    types.append(TypeDetector.TEMPORAL_DATE_TIME); colors.append('#08519c')
    
    types.append(TypeDetector.NUMERIC_INT); colors.append('#ffeda0')
    types.append(TypeDetector.NUMERIC_DOUBLE); colors.append('#fdae6b')
    
    types.append(TypeDetector.TEXTUAL); colors.append('#ef3b2c')
    types.append(TypeDetector.NULL); colors.append('#ffffff')
    
    return colors, types
    
def insight_on_single_sumary(base_name, sumary, text_profiler, numeric_profiler, geo_profiler, database=None):
    chart_base_name = base_name + '__'
    base_cols = ['Count', 'Missing', 'Unique Values', 'Top', 'Top Frequency']
    if len(geo_profiler) == 0: geo_profiler = pandas.DataFrame(columns= base_cols)
    if len(text_profiler) == 0: text_profiler = pandas.DataFrame(columns= base_cols)
    if len(numeric_profiler) == 0: numeric_profiler = pandas.DataFrame(columns= base_cols)
    
    if database is not None: print '\n\n'
    print '--- Ploting General Charts ---'
#    print 'text_profiler: \n', text_profiler
#    print 'numeric_profiler: \n', numeric_profiler
#    print 'geo_profiler: \n', geo_profiler
    
    title = 'Column Data Types with Null'
    colors, types = simple_colors_and_types()
    plot_data = ProfilerUtils.get_types_data_as_DataFrame_with_NULL_last(sumary['Types Percent'].ix[0])
    plot_data = plot_data[types]
    plot_to_file(plot_data, 'bar', title, chart_base_name + title.replace(' ', '_') + '.png', is_stacked=True
                , colors=colors)
    
    title = 'Column Data Types'
    types = types[:-1]
    colors = colors[:-1]
    plot_data = plot_data[types]
    plot_to_file(plot_data, 'bar', title, chart_base_name + title.replace(' ', '_') + '.png', is_stacked=True
                , colors=colors)
    
    colors, types = simple_colors_and_types_complete()
    title = 'Column Data Types (Detailed) with Null'
    plot_data = ProfilerUtils.get_types_data_as_DataFrame_with_NULL_last(sumary['Types Percent Complete'].ix[0])
    plot_data = plot_data[types]
    plot_to_file(plot_data, 'bar', title, chart_base_name + title.replace(' ', '_') + '.png', is_stacked=True
                , colors=colors)
    
    title = 'Column Data Types (Detailed)'
    types = types[:-1]
    colors = colors[:-1]
    plot_data = plot_data[plot_data.columns[:-1]]
    plot_to_file(plot_data, 'bar', title, chart_base_name + title.replace(' ', '_') + '.png', is_stacked=True
                , colors=colors)

    #Plot relation of column type
    title = 'Types of Columns'
    plot_data = sumary[['Columns Geo', 'Columns Numeric', 'Columns Text']]
    plot_to_file(plot_data, 'bar', title, chart_base_name + title.replace(' ', '_') + '.png', no_x_text=True)
    
    #Plot Missing Data by Columns
    plot_data = pandas.concat([text_profiler[['Count', 'Missing']],
                       numeric_profiler[['Count', 'Missing']],
                       geo_profiler[['Count', 'Missing']]
                       ])
    plot_data.columns = ['Total', 'Missing']
    plot_data = plot_data.sort('Missing')
    plot_to_file(plot_data, 'bar', 'Total/Missing Values', chart_base_name + 'plot_missing_by_column.png', 
                is_stacked=True, colormap=COLOR_RED_TO_BLUE)

    #Unique Values of Text
    plot_data = pandas.DataFrame({'Unique':text_profiler['Unique Values'], 
                                    'Total':text_profiler['Count']})
    plot_data = pandas.concat([plot_data, 
                                pandas.DataFrame({'Unique':geo_profiler['Unique Values'], 
                                                    'Total':geo_profiler['Count']})])
    plot_data = plot_data.sort('Total')
    plot_to_file(plot_data, 'bar', 'Unique Values', chart_base_name + '_plot_unique_values.png')
    
    #Uniqueness and Uniformity of Text & Geo
    plot_data = pandas.concat([text_profiler['Unique Values'] / text_profiler['Count'] * 100,
                            geo_profiler['Unique Values'] / geo_profiler['Count'] * 100,
                            numeric_profiler['Unique Values'] / numeric_profiler['Count'] * 100])
    plot_data = pandas.DataFrame({'Unique':plot_data, 'Non Unique': 100 - plot_data})
    plot_data = plot_data.sort('Unique')
    plot_to_file(plot_data, 'bar', 'Uniqueness', chart_base_name + '_plot_uniqueness.png')

                
    if database is not None:
        print '\nPloting Column Charts...'
        for col in database.columns:
            print '  ' + col
            if len(database[col].dropna()) == 0: print '   skip: empty.'; continue
            if type(database[col].dropna()[:1].values[0]) is list: print '   skip: list.'; continue
            
            plot_file = base_name + '_column_' + col
            if TypeDetector.type_of_column_data(database[col]) is TypeDetector.NUMERIC:
                plot_data = database[col]
                plot_file +='_plot_histogram.png'
                plot_to_file(plot_data, 'histogram', 'Histogram of ' + col, plot_file)
            else:
                plot_data = database[col].astype(str).value_counts()[:20]
                plot_file +='_plot_top10.png'
                plot_data.sort(ascending=False)
                plot_to_file(plot_data, 'barh', 'Top 20 values of ' + col, plot_file)
                

COLOR_RED_TO_BLUE = 'RdYlBu'
#Colormaps: 
#   http://wiki.scipy.org/Cookbook/Matplotlib/Show_colormaps
#   http://matplotlib.org/examples/color/colormaps_reference.html
def plot_to_file(plot_data, chart_kind, title, file_name, no_x_text=False, is_stacked=False, colormap=None, colors=None, sort=False, bins=20):
    plt.figure()
    if colormap is not None: colormap = colormap + '_r'
    
    if chart_kind == 'histogram':
        plot = plot_data.hist(figsize = (32, 18), xlabelsize=30, bins=bins)
        plt.ylabel("Frequency")
    
    else:
        if colors is not None:
            plot = plot_data.plot(kind = chart_kind, stacked = is_stacked, figsize = (32, 18), 
                    sort_columns=sort, color=colors)
        else:
            plot = plot_data.plot(kind = chart_kind, stacked = is_stacked, figsize = (32, 18), 
                    sort_columns=sort, colormap=colormap)
        
    if no_x_text: plt.gca().xaxis.set_major_locator(plt.NullLocator())
    title+='\n' #Cheat to make some space between the title and the chart itself

    plt.title(title, color='black', fontsize=25)
    if chart_kind != 'histogram': plt.tight_layout()
    plot.get_figure().savefig(file_name)
    
    plt.close()
    print 'Ploted: ' + title.rstrip('\n')
    print '     ', file_name
    
   
def puts(text):
    if opts['verbose']: print text

        
def process_args():
    opts = CLI.process_args(v_opts, b_opts)

    if opts['summaries'] is not None and opts['profiler'] is not None:
        raise Exception('Use "sumaries" or "profiler" option. But not both at the same time.')
    
    return opts


if __name__ == "__main__":
    ETL_BASE = '/home/danielcastellani/Documents/databases/etl-profilers/'
    CLI.ARGS = ['--verbose', 
        '--to_folder=/tmp/profilers/', 
        '--summaries=' + ETL_BASE + 'p27/_etl-profiler-summary-2014-11-14_19-56-45.csv'
#        '--profiler=' + ETL_BASE + 'p16_2014-08-26/h9gi-nx95_profiled.profiler'
    ]
    opts = process_args()
    
    if opts['summaries'] is not None:
        puts('===> Insight on Sumaries')
        insight_on_sumaries()
        generate_type_comparisson_with_metadata()
        
        title = 'map_dbs'
        data_file = opts['summaries'].replace('.csv', '_gps_dbs.csv')
        to_file = opts['to_folder'] + title +'.html'
        MapUtils.generate_map(data_file, to_file)
        
        title = 'map_rows'
        data_file = opts['summaries'].replace('.csv', '_gps_rows.csv')
        to_file = opts['to_folder'] + title +'.html'
        MapUtils.generate_map(data_file, to_file)

        
    if opts['profiler'] is not None:
        puts('===> Insight on Single Sumary')
        profiler_file_name = opts['profiler']
    
        base_name = opts['to_folder'] or FileUtils.get_file_name(profiler_file_name).strip('.json').strip('.csv')
        sumary, text_profiler, numeric_profiler, geo_profiler = ProfilerUtils.read_profiler_file(profiler_file_name)
        insight_on_single_sumary(base_name, sumary, text_profiler, numeric_profiler, geo_profiler)
        
    print '\n\n> DONE: All files ploted'
        