import json
import ConnexionMongoDB
from operator import itemgetter

############################### Connexion à MongoDB

db = ConnexionMongoDB.ConnexionDB()

############################### returns vessel

def GetVesselByName(name):  # returns a searched vessel (his name passed as a parameter)
    vessel = db.vesselExpedition.find_one({"vessel.name":name}) # vessel is a dictionary that contains the searched vessel as it is saved.
    #vessel = None
    #while vessel is not None:
        

    # A common problem with the attribute _id : his ObjectId type isn't serializable, which make it not a valid JSON format
    if vessel["_id"]:
        vessel["_id"] = str(vessel["_id"])


    result = {} # resut is a dictionnary that contains the searched vessel.
    for key, value in vessel.items():   # the function items() returns keys() combined with values()
        if (key != "_id") and (key != "actualPosition" ):
            if key == "lastPositions":
                lastPositions = []
                lastPositions.append(vessel['departurePort'].get('position').copy())
                lastPositions = lastPositions + value
                result.update({key:lastPositions})
            elif key == "nextPositions":
                nextPositions = value
                nextPositions.append(vessel['arrivalPort'].get('position').copy())
                result.update({key:nextPositions})
            else :
                result.update({key:value})
        
    return result

############################### returns all vessels

def GetAllVessels(): # returns a list of actual vessels
    vesselsList = db.vesselExpedition.find()    # vesselsList is a pymongo.cursor.Cursor class object.
    result = []  # result is a list that contains all the wanted data (it may contain duplicates, otherwise it must be a set).
    for vessel in vesselsList: # vessel is a dictionnary that contains the document reach, per each.
        vesselReturned = dict({"name":"","vesselType":""})  #vesselReturned is a dictionary that contains each vessel's actual data (name, type and positions)
        vesselReturned.update({"name":vessel.get('vessel').get('name')})
        vesselReturned.update({"vesselType":vessel.get('vessel').get('vesselType')})

        lastPositions = vessel.get("lastPositions")    # lastPositions is a list that contains each expedition's last positions
        if lastPositions:
            #date = [position["date"] for position in lastPositions]  # List Comprehension method
            #actual = (max(date))  # actual contient l'indice de la position actuelle
            #date.clear()
            actualPosition = max(lastPositions, key=itemgetter('date'))
            vesselReturned.update({"actualPosition":actualPosition})
        else:
            vesselReturned.update({"actualPosition":vessel.get('departurePort').get('position')})

        result.append(vesselReturned)

    return result

############################### Création du document depuis les ressources réparties

def InsertVessel(IMO):  # Assembles the data collected from different distributed sources, then insert it
    try :
        #period = "" #daily/hourly
        #nb = 0 #days/fromdate/todate
        #imo = IMO
        #apikey = "6eb8108c9aed56f026f6144759690adafbb39365"
        #url = f"https://services.marinetraffic.com/api/exportvesseltrack/{apikey}/v:3/period:{period}/days:{nb}/imo:{imo}/protocol:jsono"
        #rPS = request.get(url) 
        rPS = open("D:/apiflask/mongodb/retourPS01.jsono", "r")
        #ps = json.load(rPS)       # Contains the vessel coordinations, positions and stats
        ps = json.load(rPS)

        #imo = IMO
        #apikey = "1c4ce3a84d6218d552105a4e31d2cfc6f2deff22"
        #url = f"https://services.marinetraffic.com/api/voyageforecast/{apikey}/v:3/imo:{imo}/msgtype:extended/protocol:jsono"
        #rPS = request.get(url)
        #vi = json.load(rPS)
        rVI = open("D:/apiflask/mongodb/retourVI01.jsono", "r")
        vi = json.load(rVI)

        # open the image and insert it into the document (JSON object)
        #with open('C:/Users/ourib/Desktop/DAL_KALAHARI.jpg', mode='rb') as imgFile:
        #   img = imgFile.read()
        #img_str = base64.encodebytes(img).decode('utf-8')

    except Exception as ex:

        print("**************")
        print(ex)
        print("Une erreur inattendue est survenue lors de la collecte des données.")
        return "Une erreur inattendue est survenue lors de la collecte des données."

    try:
        # data variable contains a single document, collected from different PS01 calls, over a specific vessel
        data = {
            'vessel':{
                'IMO':int(ps[0]['IMO']),        # Concerning the ps returned file, each position is per line => a list of lines
                    'MMSI':int(ps[0]['MMSI']),  # rPS.json()[0]['MMSI']
                    'name':'DAL KALAHARI',
                    'vesselType':'CARGO',
                    'flag':'PT',
                    'image': "",#img_str,
                    'draughMax':int(vi[0]['DRAUGHT_MAX'])
                },
            'departurePort':{
                    'name': vi[0]['LAST_PORT'],    # Concerning the vi returned file, all positions are saved in a list containing one line
                    'position':{
                        'latitude':-33.903185705625944,
                        'longitude':18.434430940107646
                        },
                    'departurePortID':vi[0]['LAST_PORT_ID'],
                    'departurePortCode':vi[0]['LAST_PORT_UNLOCODE']
                },
            'arrivalPort':{
                'name':vi[0]['NEXT_PORT_NAME'],
                'position':{
                    'latitude':36.13672,
                    'longitude':-5.434271
                    },
                'arrivalPortID':vi[0]['NEXT_PORT_ID'],
                'arrivalPortCode':vi[0]['NEXT_PORT_UNLOCODE']
                },
            'ATD':vi[0]['LAST_PORT_TIME'],
            'ETA':vi[0]['ETA'],
            'ETACalculMT':vi[0]['ETA_CALC'],
            'distanceTravelled':vi[0]['DISTANCE_TRAVELLED'],
            'distanceRemaining':vi[0]['DISTANCE_TO_GO'],
            'lastPositions':[],
            'actualPosition':{}, # Actual position can either be the newest last position, or the very first next position. 
            'nextPositions':[]
            }
        
        # position is a variable
        position={
            'latitude':0,
            'longitude':0,
            'date':'',
            'course':0,
            'heading':0,
            'speed':0
            }

        # Insertion of historical positions from PS file
        for i in range(len(ps)):
            position['latitude'] = float(ps[i]['LAT'])
            position['longitude'] = float(ps[i]['LON'])
            position['date'] = ps[i]['TIMESTAMP']
            position['course'] = float(ps[i]['COURSE'])
            position['heading'] = float(ps[i]['HEADING'])
            position['speed'] = float(ps[i]['SPEED'])
            data['lastPositions'].append(position.copy())   # A deep copy is needed so the new position won't crush the new one
            position.clear()

        # Insertion from VI file (the received route must be adapted)
        route = vi[0]['ROUTE'].split('(')[1].split(')')[0].split(',') # route variable is a list of string couples of positions

        for i in range(len(route)):
            routePosition = route[i].split(' ')
            for elt in routePosition:   # After splitting the route, due to spaces sent from the API bought, some indesirable elements will exist that need to be eliminated
                if elt == "":
                    routePosition.remove(elt)
            
            position['latitude'] = float(routePosition[1])
            position['longitude'] = float(routePosition[0])
            data['nextPositions'].append(position.copy())   # A deep copy is needed so the new position won't crush the new one
            position.clear()

        #rVI.close()
        #rPS.close()

    except Exception as ex:

        print("**************")
        print(ex)
        print("Une erreur inattendue est survenue lors de l'assemblage du document.")
        return "Une erreur inattendue est survenue lors de l'assemblage du document."


    try:
        db.vesselExpedition.insert_one(data) # everytime, it's one document per file

    except Exception as ex:
        print("**************")
        print(ex)
        print("Une erreur inattendue est survenue lors de l'insertion.")
        return "Une erreur inattendue est survenue lors de l'insertion."
          
    return 0

###############################