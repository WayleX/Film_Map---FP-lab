"""
Module contains 3 functions used for creating maps in folium
this module creates map with 10 nearest films near your location
in a given year
Input:  year, latitude, longitude
Output: Film_Map.html
"""
import argparse
import random
from math import asin, sin, sqrt, cos
import folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderUnavailable

def distance_between_points(la_1: str,lo_1: str,la_2: str,lo_2: str) -> int:
    """
    la_1,lo_1 - lattitude and longitude of first place
    la_2,lo_2 - lattitude and longitude of second place
    Calculates distance by hoversine formula,
    returns distance in km
    >>> distance_between_points(0,0,0,0)
    0.0
    """
    radius = 6400
    la_1, lo_1, la_2, lo_2 = float(la_1)*3.14/180, float(lo_1)*3.14/180, \
        float(la_2)*3.14/180, float(lo_2)*3.14/180
    return 2*radius*asin(sqrt( (sin((la_2-la_1)/2))**2 + \
        cos(la_1)*cos(la_2)*(sin((lo_2-lo_1)/2))**2))

def helper_creator():
    """
    function creates helper file for easy search for film:
    it assigns only one location for film and ignores films outside
    of country_list countries (Almost all Europe)
    >>> helper_creator()
    None
    """
    with open('locations.list', 'r',encoding='ISO-8859-1') as file:
        country_list=['Ukraine','UK','Norway','Sweden','Finland','Estonia','Lithuania',\
            'Latvia','Poland','Slovakia','Germany','Hungary','Portugal','Spain',\
            'France','Switzerland','Italy','Croatia','Slovenia','Austria','Serbia',\
            'Greece','Bulgaria','Romania','Kosovo','Albania','Montenegro']
        useless=0
        location_list=[]
        film_list=[0]
        k=0
        for line in file:
            if useless<14:
                useless+=1
                continue
            if '{' in line:
                line=line[0:line.index('{')]+line[line.index('}')+1:]
            line=line.split(')')
            location=line[1].strip()
            if '(' in location:
                location=location[:location.index('(')].strip()
            if film_list[-1] != (line[0]+')'):
                if location.split(',')[-1].strip() in country_list:
                    film_list.append(line[0]+')')
                    location_list.append(location)
                    if k==0:
                        k=1
                        film_list.pop(0)
    count=0
    geolocator = Nominatim(user_agent="best_name_to_avoid_error")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    with open('helper_test.csv','w',encoding='utf-8') as file:
        for pos,point in enumerate(location_list):
            try:
                location = geolocator.geocode(point)
            except:
                continue
            if location is not None:
                print(point)
                file.write(film_list[pos])
                file.write(',')
                file.write(str(location.latitude))
                file.write(',')
                file.write(str(location.longitude))
                file.write('\n')

def map_creator(year:int, user_latitude: float, user_longitude: float) -> str:
    """
    Function creates map with folium library:
    user_latitude - float, given latitude
    user_longitude -float, given longitude
    year - int,  given year
    >>> map_creator(50,0,2010)
    'Created'
    """
    num_of_points = 10
    locations = [(0,0,0,9999999) for i in range(num_of_points)]
    with open('helper2.csv',encoding='utf-8') as file:
        for line in file:
            elements=line.split('),')[0] +')' , line.split('),')[1].split(',')[0],\
                 line.split('),')[1].split(',')[1].strip()
            film_name, latitude, longitude = elements
            if str(year) not in film_name:
                continue
            dist = distance_between_points(latitude, longitude, user_latitude, user_longitude)
            if dist<locations[-1][3]:
                locations.append((film_name, latitude, longitude, dist))
                locations.sort(key=lambda x: x[3])
                locations.pop(num_of_points)
    film_map = folium.Map(location=[user_latitude, user_longitude], zoom_start=6)
    films=folium.FeatureGroup(name='Nearest film locations')
    for elem in locations:
        iframe = folium.IFrame(html=elem[0],
                            width=300,
                            height=100)
        films.add_child(folium.Marker(location=[float(elem[1])+random.random()/40,
                    float(elem[2])+random.random()/40],
                    popup=folium.Popup(iframe),
                    icon=folium.Icon(color = "red")))
    film_map.add_child(films)
    folium.raster_layers.TileLayer(tiles='Stamen Toner',overlay=True).add_to(film_map)
    folium.raster_layers.TileLayer(tiles='Stamen Terrain',overlay=True).add_to(film_map)
    film_map.add_child(folium.LayerControl())
    film_map.save('Film_Map.html')
    return 'Created'

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Film in your location program')
    parser.add_argument("year", type=int, help="desired longitude")
    parser.add_argument("latitude", type=float, help="desired latitude")
    parser.add_argument("longitude", type=float, help="desired longitude")
    args = parser.parse_args()
    map_creator(args.year,args.latitude, args.longitude)
