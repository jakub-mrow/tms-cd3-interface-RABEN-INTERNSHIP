from flask import Flask
from flask import jsonify, request
from data import Data
import contman_conn as cont
import time

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

        #time the request
        start = time.clock()
        
        dataObj, loginError = cont.login(dataObj)
        if loginError is not None:
            return loginError

        # <----------------------------------------------->
        #  error handle: check if document class exists,
        #  if not return error
        # <----------------------------------------------->
        checkDocumentClass = cont.getDocumentClassID(data["documentClass"],dataObj)
        if type(checkDocumentClass) is dict:
            return checkDocumentClass

        dataObj, startError = cont.startTransaction(dataObj)
        if startError is not None:
            return startError

        dataObj, check = cont.convertFormat(data, dataObj)
        if check == False:
            return {"error": "Invalid structure of the format. One of the indexes does not exist in this document class!"}
        
        dataObj, createError = cont.createDocument(dataObj)
        if createError is not None:
            return createError

        dataObj, uploadError = cont.uploadFile(dataObj)
        if uploadError is not None:
            return uploadError

        dataObj, commitError = cont.commitTransaction(dataObj)
        if commitError is not None:
            return commitError

        dataObj, logoutError = cont.logout(dataObj)
        if logoutError is not None:
            return logoutError

        requestTime = time.clock() - start
        return {"response": "File added succefully!", "time": requestTime}, 201
        
    return {"error": "Request must be JSON"}

if __name__ == "__main__":
    app.run()