from flask import Flask, Response, request
import json
import VesselManager

###############################

app = Flask(__name__)

############################### Recherche par nom

@app.route("/Vessel_details/Name:<name>",methods=["GET"])
def Vessel_search_per_name(name):  # returns a searched vessel (his name passed as a parameter)
    try:
        result = VesselManager.GetVesselByName(name)
        return Response(
            response = json.dumps(result),
            status = 200,
            mimetype = "application/json"
        )
    except Exception as ex:
        print("**************")
        print(ex)
        print("**************")
        return Response(response = json.dumps({"message":"Une erreur inattendue est survenue concernant ce navire."}),
                        status = 500,
                        mimetype = "application/json")
        

############################### Appeler l'API putVessel

def Call_putVessel():
    try :
        resp = request.get('https://localhost:80/Document_insertion/IMO:')#<IMO>')
    except Exception as ex:
        pass
    return 0

############################### Lancer la MAP

@app.route("/Map",methods=["GET"])
def Map_call(): # returns a list of actual vessels
    try:
        result = VesselManager.GetAllVessels()
        return Response(
            response = json.dumps(result),
            status = 200,
            mimetype = "application/json"
            )
    except Exception as ex:
        print("**************")
        print(ex)
        print("**************")
        return Response(response = json.dumps({"message":"Une erreur inattendue est survenue."}), status = 500, mimetype = "application/json")
    
###############################


############################### Création du document depuis les ressources réparties

@app.route("/Document_insertion/IMO:<IMO>",methods=["GET"])
def Document_insert(IMO):  # Assembles the data collected from different distributed sources, then insert it
    try :
       result = VesselManager.InsertVessel(IMO)
       if result == 0 :
            return "Inserted succesfully !"
       else :
            return Response(response = json.dumps({"message":result}), 
                        status = 500, 
                        mimetype = "application/json")

    
    except Exception as ex:
        return Response(response = json.dumps({"message":"Problème Serveur!"}), 
                        status = 500, 
                        mimetype = "application/json")


###############################

if __name__ == "__main__":
    app.run(port=80, debug=True)


#to execute =>  python getVessel.py
