from flask import Flask
from flask import jsonify, request
from data import Data
from datetime import date
import contman_conn as cont
import time
import uuid
import logging
import os

app = Flask(__name__)

# <----------------------------------------------->
# Disable flask internal logging
# comment block below to turn it on, but it will also
# log to file additionall flask logs besides custom logs
# <----------------------------------------------->
app.logger.disabled = True
log = logging.getLogger('werkzeug')
log.disabled = True

# <----------------------------------------------->
# config for logs
# <----------------------------------------------->
logging.basicConfig(
    filename="app/logs/"+str(date.today()),
    filemode="a",
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
    encoding='utf-8'
)

@app.route("/")
def hello_world():
    return "Running"

@app.route("/documents", methods = ["POST"])
def sendFile():
    requestID = str(uuid.uuid4())
    if request.is_json:
        # <----------------------------------------------->
        # setting up data object to store repeating values
        # for requests like cookies or token
        # <----------------------------------------------->
        dataObj = Data()
        # gets request data from the user
        data = request.get_json()

        #time the request
        start = time.time()
        
        dataObj, loginError = cont.login(dataObj)
        if loginError is not None:
            logging.error("{} | {} | {}".format(requestID, "login", loginError["request-error"]))
            return loginError, loginError["request-error"][0]

        # <----------------------------------------------->
        #  error handle: check if document class exists,
        #  if not return error
        # <----------------------------------------------->
        checkDocumentClass = cont.getDocumentClassID(data["documentClass"],dataObj)
        if type(checkDocumentClass) is dict:
            logging.error("{} | {} | {}".format(requestID, "document class", checkDocumentClass["request-error"]))
            return checkDocumentClass, 400

        dataObj, startError = cont.startTransaction(dataObj)
        if startError is not None:
            logging.error("{} | {} | {}".format(requestID, "start", startError["request-error"]))
            return startError, 500

        dataObj, check = cont.convertFormat(data, dataObj)
        if check == False:
            formatError = {"request-error": "Invalid structure of the format. One of the indexes does not exist in this document class!"}
            logging.error("{} | {} | {}".format(requestID, "format", formatError["request-error"]))
            return formatError, 400
        
        dataObj, createError = cont.createDocument(dataObj)
        if createError is not None:
            logging.error("{} | {} | {}".format(requestID, "create", createError["request-error"]))
            return createError, 500

        dataObj, uploadError = cont.uploadFile(dataObj)
        if uploadError is not None:
            logging.error("{} | {} | {}".format(requestID, "upload", uploadError["request-error"]))
            return uploadError, 500

        dataObj, commitError = cont.commitTransaction(dataObj)
        if commitError is not None:
            logging.error("{} | {} | {}".format(requestID, "commit", commitError["request-error"]))
            return commitError, 500

        dataObj, logoutError = cont.logout(dataObj)
        if logoutError is not None:
            logging.error("{} | {} | {}".format(requestID, "logout", logoutError["request-error"]))
            return logoutError, 500

        requestTime = round(float(time.time() - start), 4)
        goodRes = {"response": "File added succefully!", "time": requestTime}
        logging.info("{} | {}".format(requestID, goodRes["response"]))
        return goodRes, 201

    jsonError = {"request-error": "Request must be JSON"}
    logging.error("{} | {}".format(requestID, jsonError["request-error"]))    
    return jsonError, 400

if __name__ == "__main__":
    # <----------------------------------------------->
    # create file for logging
    # <----------------------------------------------->
    dateFile = str(date.today())
    if not(os.path.isfile("logs/"+dateFile)):
        fileLog = open("logs/"+dateFile, "w+")
        fileLog.close()

    # <----------------------------------------------->
    # run the service
    # <----------------------------------------------->
    app.run(debug=True)