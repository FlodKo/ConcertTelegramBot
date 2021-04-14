import datetime
from time import  sleep

from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="test")

def Get_Location_From_String(locationString):
    location = geolocator.geocode(locationString)
    if hasattr(location, 'raw'):
        location = location.raw
        loc = [location["lat"], location['lon']]
        return loc
    else:
        return None

def Get_Address_From_Location(location):
    address = get_address_by_location(location)
    return address


def get_address_by_location(coordinates):

    try:
        sleep(1)
        address = geolocator.reverse(coordinates).raw['address']
        for key in address:
            if key == "town" or key == "city":
                typOfKey = key
            elif key == "house_number":
                house_number = key
        location = [address[typOfKey], address['road'], address['house_number']]
        return location

    except:
        return get_address_by_location(coordinates)


def String_To_Date(text):
    date_time_str = text
    try:
        date_time_obj = datetime.datetime.strptime(date_time_str, '%d.%m.%Y, %H:%M')
        return date_time_obj
    except:
        return False

def Date_To_String(date):
    strDate = date.strftime("Datum: %d.%m.%Y \nUhrzeit: %H:%M")
    return strDate