import pymongo
import os
import datetime
import json

from telegram import ( Location)
from geopy import distance
from location import Location




class DB:

    with open('config.json') as json_file:
        config = json.load(json_file)
        config = config["db"]

    myclient = pymongo.MongoClient(config["myClient"])
    mydb = myclient[config["mydb"]]
    mycol = mydb[config["mycol"]]
    myusercol = mydb[config["myusercol"]]

    def User_Point(self, update, locationName):
        loc = Location()
        loc.CreateLocation(locationName, 'adr')
        if loc.lat is not None:
            userID = update.effective_user.id
            mydict = {'User_Id': userID, 'lat': loc.lat, 'lon': loc.lat, 'name': loc.city}
            myquery = {"User_Id": userID, "name": loc.city}
            exists = self.myusercol.find(myquery)
            if exists.count() == 0:
                self.myusercol.insert_one(mydict)
                return 0
            else:
                return 1
        else:
            return 2

    def Get_User_Subscriptions(self, userId):
        myquery = {"User_Id": userId}
        userSubscriptions = self.myusercol.find(myquery)
        return userSubscriptions


    def Delete_By_Name(self, userId, name):
        for x in self.myusercol.find():
            if x['name'] == name and x['User_Id'] == userId:
                self.myusercol.delete_one(x)


    def Send_Pois(self, context, UserId):
        for x in self.myusercol.find():
            if UserId is not None:
                if UserId == x['User_Id']:
                    self.Send_Pois_By_Distance(context, x)


    def Send_Pois_By_Distance(self, context, x):
        location = (x['lat'], x['lon'])
        town = x['name']
        user_id = x['User_Id']
        today = datetime.datetime.now()
        context.bot.send_message(chat_id=user_id, text="Veranstaltungen für " + town)
        counter = 0
        for y in self.mycol.find():
            ylocation = (y['lat'], y['lon'])
            eventdistance = distance.distance(location, ylocation).km
            if eventdistance <= 20 and y['date'] > today:
                counter += 1
                text = y['name'] + "\n" + self.Date_To_String(y['date']) + "\n" + y['organizer'] + "\n" + str(y[
                    'address'])
                context.bot.send_message(chat_id=user_id, text=text)
                if y['pic'] is not False:
                    context.bot.send_photo(chat_id=user_id, photo=open("./img/" + str(y["_id"]) + ".jpg", "rb"))
        if counter == 0:
            context.bot.send_message(chat_id=user_id, text="Keine Veranstaltungen in " + town + " gefunden.")


    def insertEvent(self, context):
        event = context.user_data['event']
        mydict = {"name": event.title, "address": event.location.LocationToString(),
                  "lon": event.location.lon, "lat": event.location.lat, "artist": event.artist,
                  "genre": event.genre, "more_information": event.info, "img": event.pic,
                  "date": event.date}
        self.mycol.insert_one(mydict)
        if not os.path.exists('./img'):
            path = os.getcwd()
            os.mkdir(path + "/img")
        if event.pic is not False:
            newFile = context.bot.get_file(event.pic)
            newFile.download("img/" + str(mydict['_id']) + ".jpg")
        for x in self.mycol.find():
            print(x)


    def getEventsInRange(self, update, location, dis):
        user_location = (location.lat, location.lon)
        for x in self.mycol.find():
            event_location = (x['lat'], x['lon'])
            if distance.distance(event_location, user_location).km <= int(dis):
                update.message.reply_text(
                    x['name'] + "\n" + self.Date_To_String(x['date']) + "\n" + x['organizer'])


    def sendall(self, update):
        for x in self.mycol.find():
            update.message.reply_text(x['name'] + "\n\n" + x['organizer'])

    def DateToString(date):
        strDate = date.strtime("Datum: %d.%m.%Y \nUhrzeit: %H:%M")
        return strDate