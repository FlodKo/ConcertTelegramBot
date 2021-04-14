import geopy
from geopy.geocoders import Nominatim
from time import sleep

class Location:
    geolocator = Nominatim(user_agent="test")
    def __init__(self):
        self.lon = None
        self.lat = None
        self.street = None
        self.number = None
        self.city = None

    def CreateLocation(self, loc, ident):
        if ident == "cor":
            self.lat = str(loc[0])
            self.lon = str(loc[1])
        else:
            suc = self.GetCoordinatesByString(loc)
            if suc is False:
                return False
        self.GetAddressByCoordinates(ident)
        return True

    def GetCoordinatesByString(self, locationString):
        location = Location.geolocator.geocode(locationString)
        if hasattr(location, 'raw'):
            location = location.raw
            self.lat = location["lat"]
            self.lon = location["lon"]
            return True
        else:
            return False

    def GetAddressByCoordinates(self, ident):
        try:
            sleep(1)
            coordinates = (self.lat) +","+self.lon
            address = Location.geolocator.reverse(coordinates).raw['address']
            for key in address:
                if key == "town" or key == "city":
                    self.city = address[key]
                if ident != "cor":
                    if key == "house_number":
                        self.number = address[key]
                    if key == "street" or key =="road":
                        self.street = address[key]
            return
        except:
            return self.GetAddressByCoordinates()

    def LocationToString(self):
        string = ""
        if self.city is not None:
            string += self.city + ", "
        if self.street is not None:
            string += self.street + " "
        if self.number is not None:
            string += self.number
        return string
