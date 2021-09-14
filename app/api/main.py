from app.api.contman_conn import getClassDocumentID
from flask import Flask
from flask import jsonify, request
from data import Data
import contman_conn as cont

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "Running"

@app.route("/documents", methods = ["POST"])
def sendFile():
    if request.is_json:
        # <----------------------------------------------->
        # setting up data object to store repeating values
        # for requests like cookies or token
        # <----------------------------------------------->
        dataObj = Data()
        # gets request data from the user
        data = request.get_json()
        
        dataObj = cont.login(dataObj)

        # <----------------------------------------------->
        #  error handle: check if document class exists,
        # if not return error
        # <----------------------------------------------->
        checkDocumentClass = cont.getDocumentClassID(data["documentClass"],dataObj)
        if type(checkDocumentClass) is dict:
            return checkDocumentClass

        dataObj = cont.startTransaction(dataObj)
        dataObj, check = cont.convertFormat(data, dataObj)
        if check == False:
            return {"error": "Invalid structure of the format. One of the indexes does not exist in this document class!"}
        dataObj = cont.createDocument(dataObj)
        dataObj = cont.uploadFile(dataObj)
        dataObj = cont.commitTransaction(dataObj)
        dataObj = cont.logout(dataObj)
        return {"response": "File added succefully!"}, 201
        
    return {"error": "Request must be JSON"}

if __name__ == "__main__":
    app.run()