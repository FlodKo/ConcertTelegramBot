import datetime
from location import Location
import processingData as pD


class Event:
    def __init__(self):
        self.title = None
        self.date = None
        self.location = None
        self.genre = None
        self.artist = None
        self.pic = None
        self.info = None


    def AddTitle(self, title):
        self.title = title

    def AddDate(self, date):
        dateTimeStr = date
        try:
            dateTimeObj = datetime.datetime.strptime(dateTimeStr, '%d.%m.%Y, %H:%M')
            suc = True
        except:
            suc = False
        if suc is not False:
            self.date = dateTimeObj
            return True
        else:
            return False

    def AddGenre(self, genre):
        self.genre = genre

    def AddLocation(self, location, ident):
        self.location = Location()
        suc = self.location.CreateLocation(location, ident)
        return suc

    def AddArtist(self, artist):
        self.artist = artist

    def AddPic(self, pic):
        self.pic = pic

    def AddInfo(self, info):
        self.info = info
