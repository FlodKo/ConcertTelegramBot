import telegram.ext
import datetime
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, PicklePersistence)
from telegram import (ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, Location, KeyboardButton)
from event import Event
from location import Location
from db import DB



# !/usr/bin/python
# ''-*- coding:utf-8 -*-

class BOT():
    def __init__(self, token):
        # Variablen
        self.token = token

        # Datenbankobjekt

        # States
        self.CHOOSING, self.GET_EVENT_NAME, self.GET_EVENT_GENRE, self.GET_EVENT_LOCATION, self.GET_EVENT_ARTIST, \
        self.GET_EVENT_MORE_INFORMATION, self.GET_EVENT_IMG, self.GET_EVENTS_IN_RANGE, self.GET_USER_LOCATION, \
        self.GET_EVENT_DATE, self.GET_USER_POI, self.SUBSCRIBE_CHOOSING, self.SUBSCRIBE_DELETE = range(13)
        self.DB = DB()

        # Keyboards and Buttons

        # Choosing-Keybord
        self.choosing_keys = [['Veranstaltung melden'], ['Zeige mir Veranstaltungen in der Nähe'], ['Abonierte Orte'],
                              ['Bot beenden']]
        self.choosing_keyboard = ReplyKeyboardMarkup(self.choosing_keys, one_time_keyboard=True)

        self.skip_keys = [['Überspringen'], ['Abbrechen']]
        self.skip_keyboard = ReplyKeyboardMarkup(self.skip_keys, one_time_keyboard=True)

        # Event_Genre-Keyboard
        self.event_genre_keys = [['Pop'], ['Punk'], ['Rock'], ['Hip-Hop'], ['Rap'],
                                ['Abbrechen']]
        self.event_genre_keyboard = ReplyKeyboardMarkup(self.event_genre_keys, one_time_keyboard=True)

        self.subscibed_location_keys = [["Ort abonieren"], ['Veransaltungen in deinen Orten anzeigen'],
                                        ["Abonierte Orte löschen"], ["Zurück"]]
        self.subscibed_location_keboard = ReplyKeyboardMarkup(self.subscibed_location_keys, one_time_keyboard=True)

        self.cancle_keyboard = ReplyKeyboardMarkup([['Abbrechen']])

    # start -> CHOOSING
    def Start(self, update, context):
        reply = "Du bist im Startmenü"
        update.message.reply_text(reply, reply_markup=self.choosing_keyboard)
        return self.CHOOSING

    # CHOOSING -> Report -> GET_EVENT_TITLE
    def Report(self, update, context):
        reply = "Wie heißt die Veranstaltung?\n(Gib einen Text ein)"
        update.message.reply_text(reply, reply_markup=self.cancle_keyboard)
        return self.GET_EVENT_NAME

    def Ask_For_Distance(self, update, context):
        reply = "Du kannst jetzt eine Entfernung (in Kilometern) festlegen, innerhalb der alle Veranstaltungen " \
                "angezeigt werden. "
        update.message.reply_text(reply, reply_markup=self.cancle_keyboard)
        return self.GET_USER_LOCATION

    def Ask_For_User_Location(self, update, context):
        if update.message.text.isnumeric():
            context.user_data['distance'] = update.message.text
            reply = "Du hast " + context.user_data[
                'distance'] + " als Distanz gewählt. \n\n Gib jetzt einen Standort ein."
            update.message.reply_text(reply, reply_markup=self.cancle_keyboard)
            return self.GET_EVENTS_IN_RANGE
        else:
            update.message.reply_text("Das war keine Zahl, gib eine Zahl ein.", reply_markup=self.cancle_keyboard)
            return self.GET_USER_LOCATION
    #Todo Zu einer Funktion zusammenlegen und Objektorientiert schreiben

    def Get_User_Location(self, update, context):
        distance = context.user_data['distance']
        location = Location()
        if update.message.location is not None:
            loc = update.message.location.latitude, update.message.location.longitude
            suc = location.CreateLocation(loc, "cor")
        else:
            loc = update.message.text
            suc = location.CreateLocation(loc, "adr")
        if suc is True:
            reply = "Das waren alle Veranstaltungen im Radius von " + context.user_data['distance'] + " Kilometern."
            self.DB.getEventsInRange(update, location, distance)
            update.message.reply_text(reply, reply_markup=self.choosing_keyboard)
            return self.CHOOSING
        else:
            update.message.reply_text("Das war keine gültige Adresse, versuch es nochmal")
            return self.GET_EVENTS_IN_RANGE

    # GET_EVENT_TITLE -> Get_Title -> CHOOSING
    def Get_Name(self, update, context):
        event = Event()
        event.AddTitle(update.message.text)
        context.user_data['event'] = event
        reply = "Super du hast\"" + update.message.text + "\"als Titel gewählt \n\nWann findet die " \
                                                          "Veranstaltung statt? Gib Zeit und Datum bitte in diesem " \
                                                          "Format an: TT:MM:YYYY, HH:MM, also zum Beispiel " \
                                                          "12.12.2020, 20:00"
        update.message.reply_text(reply, reply_markup=self.cancle_keyboard)
        return self.GET_EVENT_DATE

    def Get_Date(self, update, context):
        suc = context.user_data['event'].AddDate(update.message.text)
        if suc:
            reply = "Super du hast\"" + update.message.text + "\"als Datum der Veranstaltung gewählt.\n\n Welches " \
                                                              "Genre hat die Veranstaltung?"
            update.message.reply_text(reply, reply_markup=self.event_genre_keyboard)
            return self.GET_EVENT_GENRE
        else:
            update.message.reply_text("Das war nicht das richrige Format, du musst dich leider genau an das Format "
                                      "halten.")
            return self.GET_EVENT_DATE

    def Get_Genre(self, update, context):
        context.user_data['event'].AddGenre(update.message.text)
        reply = "Super du hast\"" + update.message.text + "\"als Genre der Veranstaltung gewählt \n\nWo findet die " \
                                                          "Veranstaltung statt? Du kannst einen Standort teilen um " \
                                                          "die Location anzugeben (muss nicht dein eigener sein)." \
                                                          "Alternativ kannst du auch eine Adresse angeben. "
        update.message.reply_text(reply, reply_markup=self.cancle_keyboard)
        return self.GET_EVENT_LOCATION

    def Get_Location(self, update, context):
        if update.message.location is not None:
            loc = update.message.location.latitude, update.message.location.longitude
            suc =context.user_data['event'].AddLocation(loc, "cor")
        else:
            loc = update.message.text
            suc = context.user_data['event'].AddLocation(loc, "adr")
        if suc is True:
            reply = "Super, du hast eine Location ausgewählt!. Wer tritt auf der Veranstaltung auf?"
            update.message.reply_text(reply)
            return self.GET_EVENT_ARTIST
        reply = "Das war keine gültige Eingabe. Überprüfe die Rechtschreibung der Adresse und Verusche es nochmal."

        update.message.reply_text(reply)
        return self.GET_EVENT_LOCATION


    def Get_Event_Artist(self, update, context):
        context.user_data['event'].AddArtist(update.message.text)
        reply = "Super, du hast " + update.message.text + "als Künstler der Veranstaltung festgelegt.\n\n Jetzt " \
                                                          "hast du die Möglichkeit noch weitere Informationen zur " \
                                                          "Veranstlatung (in Textform) einzugeben. "
        update.message.reply_text(reply, reply_markup=self.skip_keyboard)
        return self.GET_EVENT_MORE_INFORMATION

    def Get_More_Information(self, update, context):
        if update.message.text != "Überspringen":
            context.user_data['event'].AddInfo(update.message.text)
        reply = "Jetzt kannst du noch ein Bild als Quelle hinzufügen."
        update.message.reply_text(reply, reply_markup=self.skip_keyboard)
        return self.GET_EVENT_IMG

    def Get_Img(self, update, context):
        if update.message.text == "Überspringen":
            context.user_data['event'].AddPic(False)
            reply = "Du hast die Veranstaltung erfolgreich gemeldet. Vielen Dank!"
        elif update.message.photo[0] is not None:
            context.user_data['event'].AddPic(update.message.photo[0].file_id)
            reply = "Du hast ein Bild hinzugefügt und die Veranstaltung erfolgreich gemeldet. Vielen Dank!"
        self.DB.insertEvent(context)
        update.message.reply_text(reply, reply_markup=self.choosing_keyboard)
        return self.CHOOSING

    def Subscribe_Menu(self, update, context):
        reply = "Hier kannst du Veranstaltungen in deinen abonierten Orte anzeigen, die Orte löschem oder neue " \
                "Hinzufügen."
        update.message.reply_text(reply, reply_markup=self.subscibed_location_keboard)
        return self.SUBSCRIBE_CHOOSING

    def Subscribe_Ask_For_Location(self, update, context):
        reply = "Gib den Namen einer Stadt ein, du wirst dann automatisch benachrichtigt, wenn dort oder in der Nähe " \
                "Veranstaltungen stattfinden. "
        update.message.reply_text(reply, reply_markup=self.cancle_keyboard)
        return self.GET_USER_POI

    def Subscribe_Get_Location(self, update, context):
        location = update.message.text
        check = self.DB.User_Point(update, location)
        if check == 0:
            reply = "Du hast einen Ort aboniert."
            update.message.reply_text(reply, reply_markup=self.subscibed_location_keboard)
            return self.SUBSCRIBE_CHOOSING
        if check == 1:
            reply = "Du hast diesen Ort schon aboniert. Du bist wieder im Abonements-Menü"
            update.message.reply_text(reply, reply_markup=self.subscibed_location_keboard)
            return self.SUBSCRIBE_CHOOSING
        else:
            reply = "Das war kein gültiger Ortsname, versuch es nochmal."
            update.message.reply_text(reply, reply_markup=self.cancle_keyboard)
            return self.GET_USER_POI

    def Send_Abonements(self, update, context):
        UserId = update.effective_user.id
        self.DB.Send_Pois(context, UserId)
        update.message.reply_text("Das waren alle Veranstaltungen in den Orten, die du aboniert hast",
                                  reply_markup=self.subscibed_location_keboard)
        return self.SUBSCRIBE_CHOOSING

    def Show_Subscribed_Locations(self, update, context):
        reply_text = 'Wähle einen Punkt, um ihn zu löschen'
        allPoisKeyboard = []
        data = self.DB.Get_User_Subscriptions(update.effective_user.id)
        if data.count() == 0:
            update.message.reply_text(
                'Keine Punkte', reply_markup=self.subscibed_location_keboard)
            return self.SUBSCRIBE_CHOOSING
        for date in data:
            allPoisKeyboard.append([date['name']])
        editMarkup = ReplyKeyboardMarkup(allPoisKeyboard, one_time_keyboard=True)
        update.message.reply_text(
            reply_text, reply_markup=editMarkup)
        return self.SUBSCRIBE_DELETE

    def Delete_Subscibed_Location(self, update, context):
        name = update.message.text
        userId = update.effective_user.id
        self.DB.Delete_By_Name(userId, name)
        reply = "Du hast " + name + " gelöscht."
        update.message.reply_text(reply, reply_markup=self.subscibed_location_keboard)
        return self.SUBSCRIBE_CHOOSING

    def Done(self, update, context):
        update.message.reply_text(
            "Bis bald!", reply_markup=ReplyKeyboardMarkup([['/start']], resize_keyboard=True, one_time_keyboard=True))
        return ConversationHandler.END

    def Cancle(self, update, context):
        choosing = update.message.text
        if choosing == "Zurück":
            reply = "Du bist wieder im Hauptmenü"
        if choosing == "Abbrechen":
            reply = "Du hast die hast den Meldevorgang abgebrochen und bist wieder im Hauptmenü"
        update.message.reply_text(reply, reply_markup=self.choosing_keyboard)
        return self.CHOOSING

    def callback_daily(self, context: telegram.ext.CallbackContext):
        UserId = None
        self.DB.Send_Pois(context, UserId)

    # MAIN
    def Main(self):
        # Persistence and init token
        pp = PicklePersistence(filename='conversationbot')
        updater = Updater(self.token, persistence=pp, use_context=True)
        dp = updater.dispatcher
        jq = updater.job_queue
        job_daily = jq.run_daily(self.callback_daily, time=datetime.time(23, 0, 00), )
        conversation_handler = ConversationHandler(
            entry_points=[CommandHandler(
                'start', self.Start)],

            states={
                self.CHOOSING: [
                    MessageHandler(Filters.regex('^Veranstaltung melden'),
                                   self.Report),
                    MessageHandler(Filters.regex('^Zeige mir Veranstaltungen in der Nähe'),
                                   self.Ask_For_Distance),
                    MessageHandler(Filters.regex('^Abonierte Orte'),
                                   self.Subscribe_Menu),
                ],
                self.GET_USER_POI: [
                    MessageHandler(Filters.text,
                                   self.Subscribe_Get_Location)
                ],
                self.SUBSCRIBE_CHOOSING: [
                    MessageHandler(Filters.regex('^Ort abonieren'),
                                   self.Subscribe_Ask_For_Location),
                    MessageHandler(Filters.regex('^Veransaltungen in deinen Orten anzeigen'),
                                   self.Send_Abonements),
                    MessageHandler(Filters.regex('^Abonierte Orte löschen'),
                                   self.Show_Subscribed_Locations),
                    MessageHandler(Filters.regex('^Zurück'),
                                   self.Cancle)
                ],
                self.SUBSCRIBE_DELETE: [
                    MessageHandler(Filters.text,
                                   self.Delete_Subscibed_Location)
                ],
                self.GET_EVENT_NAME: [
                    MessageHandler(Filters.text,
                                   self.Get_Name),
                ],
                self.GET_EVENT_DATE: [
                    MessageHandler(Filters.regex('Abbrechen'),
                                   self.Cancle),
                    MessageHandler(Filters.text,
                                   self.Get_Date)
                ],
                self.GET_EVENT_GENRE: [
                    MessageHandler(Filters.regex('Abbrechen'),
                                   self.Cancle),
                    MessageHandler(Filters.text,
                                   self.Get_Genre)
                ],
                self.GET_EVENT_LOCATION: [
                    MessageHandler(Filters.regex('Abbrechen'),
                                   self.Cancle),
                    MessageHandler(Filters.text,
                                   self.Get_Location),
                    MessageHandler(Filters.location,
                                   self.Get_Location)
                ],
                self.GET_EVENT_ARTIST: [
                    MessageHandler(Filters.regex('Abbrechen'),
                                   self.Cancle),
                    MessageHandler(Filters.text,
                                   self.Get_Event_Artist)
                ],
                self.GET_EVENT_MORE_INFORMATION: [
                    MessageHandler(Filters.regex('Abbrechen'),
                                   self.Cancle),
                    MessageHandler(Filters.text,
                                   self.Get_More_Information)
                ],
                self.GET_EVENT_IMG: [
                    MessageHandler(Filters.regex('Abbrechen'),
                                   self.Cancle),
                    MessageHandler(Filters.photo,
                                   self.Get_Img),
                    MessageHandler(Filters.regex('Überspringen'),
                                   self.Get_Img)
                ],
                self.GET_EVENTS_IN_RANGE: [
                    MessageHandler(Filters.regex('Abbrechen'),
                                   self.Cancle),
                    MessageHandler(Filters.location,
                                   self.Get_User_Location),
                    MessageHandler(Filters.text,
                                   self.Get_User_Location)
                ],
                self.GET_USER_LOCATION: [
                    MessageHandler(Filters.regex('Abbrechen'),
                                   self.Cancle),
                    MessageHandler(Filters.text,
                                   self.Ask_For_User_Location)
                ],

            },

            fallbacks=[
                MessageHandler(Filters.regex('Bot beenden$'),
                               self.Done),
                MessageHandler(Filters.regex('Abbrechen'),
                               self.Cancle)
            ],
            name="my_play_conversation",
            persistent=True
        )

        dp.add_handler(conversation_handler, group=0)
        updater.start_polling()
        updater.idle()