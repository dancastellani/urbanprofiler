# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="danielcastellani"
__date__ ="$Jun 26, 2014 6:46:00 PM$"

# requires netcdf4-python (netcdf4-python.googlecode.com)
import numpy as np
import matplotlib.pyplot as plt
import pandas
import utils.FileUtils as FileUtils 
import datetime

BORDER = 0.001

def plot_map(map_data):    
    plt.figure(figsize = (16, 9)) # my screensize
#    plt.figure(figsize = (48, 27)) # large


    # llcrnrlat,llcrnrlon,urcrnrlat,urcrnrlon
    # are the lat/lon values of the lower left and upper right corners
    # of the map.
    # lat_ts is the latitude of true scale.
    # resolution = 'c' means use crude resolution coastlines.
    
#    llcrnrlat=-80; urcrnrlat=80; llcrnrlon=-180; urcrnrlon=180 #Defaults
    
    llcrnrlon = map_data.long.astype(float).min()
    llcrnrlat = map_data.lat.astype(float).min()
    urcrnrlon = map_data.long.astype(float).max()
    urcrnrlat = map_data.lat.astype(float).max()
    
    #Limit to NYC
#    ll = 40.473594, -74.368018
#    ur = 41.014105, -73.630561
    llcrnrlon = -74.368018; llcrnrlat = 40.473594; urcrnrlon = -73.630561; urcrnrlat = 41.014105
    
    #Center of map
    center_long = np.mean([urcrnrlon, llcrnrlon])
    center_lat = np.mean([urcrnrlat, llcrnrlat])
    
    #Expand the border
#    llcrnrlat -= BORDER; llcrnrlon -= BORDER; urcrnrlat += BORDER; urcrnrlon += BORDER
    
    print 'Creating Map'
    map = Basemap(projection='merc',llcrnrlat=llcrnrlat,urcrnrlat=urcrnrlat,
                llcrnrlon=llcrnrlon,urcrnrlon=urcrnrlon,lat_ts=20, resolution='h', area_thresh = 0.1)
                
    map.drawcoastlines()
    map.drawrivers()
    map.drawcountries()
    map.fillcontinents(color='coral')
    map.drawparallels(np.arange(-90.,91.,30.))
    map.drawmeridians(np.arange(-180.,181.,60.))
    map.drawmapboundary(fill_color='aqua')
#    map.bluemarble()
    
    print 'Processing points'
    xpt,ypt = map(list(map_data.long), list(map_data.lat))
    
    print 'Ploting on map'
    colors = 'bo'
    map.plot(xpt, ypt, colors, markersize=1)
    
#    print 'Plot center of map'
#    center_long, center_lat = map(center_long, center_lat)
#    map.plot(center_long, center_lat, 'ro', markersize=20)
    
    print 'Showing map'
    plt.title("Mercator Projection")
    plt.tight_layout()
    plt.show()
    
    print 'Map Closed'
    
    
def generate_google_maps_html(data, to_file, title = 'GPS Heatmap and Points', precision = 5):
    template = open('../resources/google-map-template.html', 'r')
    sprecision = str(precision)
    to_file.rstrip('.html')
    to_file += '_p.' + sprecision + 'f.html'
    map_file = open(to_file, 'w+')
    
    if 'lat' not in data.columns or 'long' not in data.columns:
        print 'Generating lat, long from gps'
        data['lat'] = data['long'] = 1
        data.lat=data.gps.str.rstrip(')').str.lstrip('(').apply(lambda x: x.split(',')[0])
        data.long=data.gps.str.rstrip(')').str.lstrip('(').apply(lambda x: x.split(',')[1])
        
    #view: http://en.wikipedia.org/wiki/Decimal_degrees
    print 'Reducing precision of lat and long to .{0}f (1 meter is .5f)...'.format(sprecision)
    temp = data[['lat', 'long', 'count']];
    precision_string = '{0:.' + sprecision + 'f}'
    temp.lat = temp.lat.astype(float).apply(lambda x: precision_string.format(x))
    temp.long = temp.long.astype(float).apply(lambda x: precision_string.format(x))
    temp = temp[['lat', 'long', 'count']].groupby(['lat', 'long']).sum()
    temp = temp.reset_index()
    
    print 'Processing points'
    temp['cmd'] = '    {location: new google.maps.LatLng(' + temp.lat.astype(str) + ', ' + temp.long.astype(str) \
        + '), weight:' + temp['count'].astype(str) + ' }'

    print 'Writing file'
    for line in template.readlines():
#        map_file.write(line)
        if '//DATA_TO_PLOT' in line  :
            print 'Inserting points'
            for cmd in temp.cmd:
                map_file.write(cmd + ',\n')
        
        elif 'center: new google.maps.LatLng(40.743849, -73.999289),' in line:
            center_lat = np.mean([float(temp.lat.min()), float(temp.lat.max())])
            center_long = np.mean([float(temp.long.min()), float(temp.long.max())])
            map_file.write('center: new google.maps.LatLng({0}, {1}),\n'.format(center_lat, center_long))
        
        elif '<<<MAP_TITLE>>>' in line:
            map_file.write('\t<b>Profiler Map: {0}</b>\n'.format(title))
            
        elif '<<<Points>>>' in line:
            map_file.write('\t<br/><spam id="id_points"><b>Points:</b> {0:,} <b>Records:</b> {1:,} <b>GPS Precision:</b> .{2}f</spam>\n'.format(len(temp), temp['count'].sum(),sprecision))
        
        else:
            map_file.write(line)
    
    print 'Closing file'
    map_file.close()
    print 'Generated file: ', to_file, '    @', datetime.datetime.now()
    

PRECISION_TEN_METERS = 4
PRECISION_ONE_METER = 5

def generate_map(data_file, to_file, precision=PRECISION_ONE_METER):
#    title = 'GPS rows (as DBs) - 2014-06-25 - 22-05-34'
    title = FileUtils.get_file_name(data_file)
    
    map_data = pandas.read_csv(data_file)
    map_data.columns = ['gps', 'count']
    generate_google_maps_html(map_data[:], to_file, title, precision= precision)
#    plot_map(map_data[:])

    print 'Done.'

if __name__ == "__main__":
    data_file = '/home/danielcastellani/Documents/databases/etl-profilers/p23_2014-11-04/_etl-profiler-summary-2014-11-04_15-13-26_gps_dbs.csv'
    to_file = '/tmp/profilers/heatmap_p4_dbs'
    
    generate_map(data_file, to_file)
    