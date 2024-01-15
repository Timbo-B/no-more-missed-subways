from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToDict
import requests
import time
import datetime
import time
from datetime import datetime
import json



class subwayFetch:
    def __init__(self):
        self.NQRWfeed = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw' # N,Q,R,W 
        self.BDFMfeed = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm' # B,D,F,M
        self.S123456feed = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs' # 1,2,3,4,5,6,7
        self.ACEHfeed = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace' # A,C,E,H 
        self.Lfeed = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l' # L
        self.Gfeed = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g' # G 
        self.JZfeed = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz' # JZ 
        self.SIRfeed = 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-si' # SIR
        self.feeds = [self.NQRWfeed, self.BDFMfeed, self.S123456feed, self.ACEHfeed, self.Lfeed, self.Gfeed, self.JZfeed, self.SIRfeed]
        self.stations = json.load(open('stations.json'))
        self.apiKey = open("key.txt", "r").read()

    def getStopID(self, nameStr, direction, route):
        for station in self.stations:
            if ((station['name'] == nameStr) & (station['routeId'] == str(route))):
                if direction == 'uptown':
                    return str(station['stop_id']) + 'N'
                elif direction == 'downtown':
                    return str(station['stop_id']) + 'S'
                else:
                    raise Exception('direction gotta be uptown or downtown')
        raise Exception('name not found')

    def getTimes(self,feed):        
        # Request parameters
        headers = {'x-api-key': self.apiKey}
        
        # Get the train data from the MTA
        response = requests.get(feed, headers=headers, timeout=30)

        # Parse the protocol buffer that is returned
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)

        # Get a list of all the train data
        subway_feed = MessageToDict(feed)
        realtime_data = subway_feed['entity'] # train_data is a list

        # A list of all the arrivals we found for our station in the given feed
        arrivals = []
        # Iterate over each train arrival
        try:
            for train in realtime_data:
                # If there is a trip update with a stop time update
                if train.get('tripUpdate'):
                    routeId = train['tripUpdate']['trip']['routeId']
                    if (train['tripUpdate'].get('stopTimeUpdate')):
                        # get for each stop time update that is at our stop
                        for update in train['tripUpdate'].get('stopTimeUpdate'):

                            # checking for the arrival/departure keys; these keys are missing at the last stops of the line
                            if update.get('arrival'):
                                trainTime = update['arrival']['time']
                            elif update.get('departure'): 
                                trainTime = update['departure']['time']
                            else:
                                continue
                            
                            # Get the number of seconds from now to the arrival time
                            timeDelta = int(trainTime)-time.mktime(datetime.now().timetuple())

                            # If we alredy missed it, skip it
                            if (timeDelta < 0):
                                continue
                                                
                            # Calculate minutes and seconds until arrival
                            timeDeltaMin = int(timeDelta / 60)

                            timeDeltaSec = int(timeDelta % 60)

                            # Round to nearest minute
                            if (timeDeltaSec > 30):
                                timeDeltaMin = timeDeltaMin + 1

                            # Skips zeros
                            if (timeDeltaMin == 0):
                                continue
                            
                            # departureUnix = int(update['departure']['time'])
                            arrivalUnix = int(trainTime)

                            update['arrivalTime'] = datetime.fromtimestamp(arrivalUnix).strftime("%H:%M:%S")
                            # update['departure'] = datetime.fromtimestamp(departureUnix).strftime("%H:%M:%S")
                            update['minArrival'] = timeDeltaMin
                            update['routeId'] = routeId
                                    
                            arrivals.append(update)
        except:
            raise Exception('mta api fetch error')
        return arrivals
    
    def getAllArrivals(self):
        arrivals = []
        for feed in self.feeds:
            arrivals.extend(self.getTimes(feed))
        return arrivals

    def getArrivalStr(self, stopName, direction, route, arrivals, getNextNum = 3):
        arrivalsSort = arrivals.copy()
        selStop = self.getStopID(stopName, direction, route)
        arrivalsStop = [stop['minArrival'] for stop in arrivalsSort if ((stop['stopId'] == selStop) & (stop['routeId'] == route))]
        displayStr = ''
        selArrivals = arrivalsStop[0:getNextNum].copy()
        for arrivalInd, arrival in enumerate(selArrivals):
            if arrivalInd < len(selArrivals) -1:
                displayStr = displayStr + str(arrival) + ' min, '
            else:
                displayStr = displayStr + str(arrival) + ' min'
        return displayStr
