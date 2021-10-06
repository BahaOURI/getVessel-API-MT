from os import system
import pymongo

############################### Connexion à MongoDB
def ConnexionDB():
    system('net start mongodb')
    try :
        mongo = pymongo.MongoClient(
            host="localhost",
            port=27017,
            serverSelectionTimeoutMS = 4000 #Setup Connection failure to 4 second timeout
            )
        db = mongo.Manitoo     # Connect to the DB
        mongo.server_info() # Trigger exception if cannot connect to mongoDB
    except Exception as ex:
        print ("Error - Cannot Connect to DB")
        print (ex)
    return db
