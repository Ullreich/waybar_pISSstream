from lightstreamer.client import *
import datetime
import time
import pytz

class Info:
    def __init__(self):
        self.piss_volume = 0
        self.current_time = datetime.datetime.now()
        self.current_year = datetime.datetime.now().year
        self.iss_time = 0
        self.iss_year = datetime.datetime.now().year
    
    def time_conversion(self, time):
        pass

Info = Info()

def set_timezone(dt):
    # Create a timezone object
    timezone = pytz.timezone("Europe/London")
    # Localize the datetime object to the specified timezone
    localized_dt = timezone.localize(dt)
    return localized_dt

def year_to_unix(year):
    # Create a datetime object for January 1st of the given year
    dt = datetime.datetime(year, 1, 1)
    # Set the timezone
    new_dt = set_timezone(dt)
    # Convert the datetime object to a Unix timestamp
    unix_time = int(new_dt.timestamp())
    return unix_time

def TS_to_GMT(tsu):
    ts_str = tsu.encode('ascii', 'ignore')
    ts = float( ts_str )  
    ts_day = int(ts/24)
    ts_hour = int(((ts/24)-ts_day)*24)
    ts_minute = int((((ts/24)-ts_day)*24-ts_hour)*60)
    ts_seconds = int(((((((ts/24)-ts_day)*24-ts_hour)*60) - ts_minute)*60))
    return ("GMT " + str(ts_day) + "/" + str(ts_hour) + ":" + str(ts_minute) + ":" + str(ts_seconds))

def last_updated():
    pass

# A class implementing the SubscriptionListener interface
class SubListener:
    def __init__(self, Info):
        self.Info = Info

    def onItemUpdate(self, update):
        pass
    def onClearSnapshot(self, itemName, itemPos):
        pass
    def onCommandSecondLevelItemLostUpdates(self, lostUpdates, key):
        pass
    def onCommandSecondLevelSubscriptionError(self, code, message, key):
        pass
    def onEndOfSnapshot(self, itemName, itemPos):
        pass
    def onItemLostUpdates(self, itemName, itemPos, lostUpdates):
        pass
    def onListenEnd(self):
        pass
    def onListenStart(self):
        pass
    def onSubscription(self):
        pass
    def onSubscriptionError(self, code, message):
        pass
    def onUnsubscription(self):
        pass
    def onRealMaxFrequency(self, frequency):
        pass

class PisstankSubListener(SubListener):
    def onItemUpdate(self, update):
        #print(f"Value: {update.getValue("Value")} Status: {update.getValue("Status")} Time: {TS_to_GMT(update.getValue("TimeStamp"))}");
        piss_volume = update.getValue("Value")
        print(f"Percentage filled: {piss_volume}%. Measurement from: {TS_to_GMT(update.getValue("TimeStamp"))}");
        timestamp_unix = int((float(update.getValue("TimeStamp"))-24)*60*60);
        year = int(self.Info.iss_year)
        unix_time = year_to_unix(year)+timestamp_unix
        time_diff = int(time.time())-unix_time
        stringified_time = datetime.timedelta(seconds=time_diff)
        print(f"time since last update: {stringified_time}")

        self.Info.iss_time = unix_time
        self.Info.piss_volume = piss_volume
    
class TimeSubListener(SubListener):
    def onItemUpdate(self, update):
        ##print(f"Time {update.getValue("Value")} Status.Class: {update.getValue("Status.Class")} Status: {update.getValue("Status")}");
        self.Info.iss_year = update.getValue("Value")    

def wait_for_input():
    input("{0:-^80}\n".format("HIT CR TO UNSUBSCRIBE AND DISCONNECT FROM LIGHTSTREAMER"))

loggerProvider = ConsoleLoggerProvider(ConsoleLogLevel.WARN)
LightstreamerClient.setLoggerProvider(loggerProvider)

lightstreamer_client = LightstreamerClient("http://push.lightstreamer.com", "ISSLIVE")
lightstreamer_client.connect()

pisstank = Subscription(
    mode="MERGE",
    items=["NODE3000005"],
    fields=["Value", "Status", "TimeStamp"]
)

ISStime = Subscription(
    mode="MERGE",
    items=["TIME_000002"],
    fields=["Value", "Status.Class", "Status", "TimeStamp"]
)

# Adding the subscription listener to get notifications about new updates
pisstank.addListener(PisstankSubListener(Info))
ISStime.addListener(TimeSubListener(Info))

# Registering the Subscription
lightstreamer_client.subscribe(pisstank)
lightstreamer_client.subscribe(ISStime)

wait_for_input()

# Unsubscribing from Lightstreamer by using the subscription as key
lightstreamer_client.unsubscribe(pisstank)
lightstreamer_client.unsubscribe(ISStime)

# Disconnecting
lightstreamer_client.disconnect()