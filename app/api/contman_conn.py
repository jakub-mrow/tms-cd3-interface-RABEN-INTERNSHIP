import requests
import json
from data import Data
import pprint
import os
import sys

# <----------------------------------------------->
# DEBUG MODE
# If you want to see prints, set variable debug to True,
# if False nothing will be shown
#
# If there is an error in a response,
# body of the reponse will always be printed
# <----------------------------------------------->
debug = True
def log(message, debug):
        if debug == True:
                print(message)

# <----------------------------------------------------------->
# Terminology:
# - document class
# - document
# - index 
#
# 6 requests to send a file to Contman system
# search for functions to get to them fast
# 1. Logging to contman
# 2. Starting transaction
# 3. Creating document
# 4. Uploading file to the document
# 5. Commiting/finishing the transaction
# 6. Logging out
# <----------------------------------------------------------->


# <----------------------------------------------->
# Helper functions (start)

def parseJson(data):
        parsed = json.loads(data)
        prettyParsed = json.dumps(parsed, indent=4, sort_keys=True)
        return prettyParsed

def parseHeaders(headers):
        return parseJson(json.dumps(dict(headers)))

# <----------------------------------------------->
# Sending a request to postman api to search for
# document class ID based on class name
# <----------------------------------------------->
def getClassDocumentID(className, dataObj):
        print("Getting classDocumentID")
        className.replace(" ", "%20")
        URL = "http://cd3tstapp.raben-group.com/api/global/classes/{}".format(className)
        headers = {
                "Cookie": dataObj.cookies,
                "Accept": "application/json",
                "Content-type": "application/json",
                "Authorization": dataObj.token
        }

        res = requests.get(URL, headers=headers)
        code = int(res.status_code)
        print("Status code: {}".format(code))

        if code == 200:
                categoryName = res.json()["id"]
                return categoryName

# <----------------------------------------------->
# Sending a request to postman api to search for
# categoryID based on category name
# <----------------------------------------------->
def getCategoryID(categoryName, dataObj):
        print("Getting categoryDocumentID")
        categoryName.replace(" ", "%20")
        URL = "http://cd3tstapp.raben-group.com/api/global/categories/{}".format(categoryName)
        headers = {
                "Cookie": dataObj.cookies,
                "Accept": "application/json",
                "Content-type": "application/json",
                "Authorization": dataObj.token
        }
        res = requests.get(URL, headers=headers)
        code = int(res.status_code)
        print("Status code: {}".format(code))

        if code == 200:
                categoryID = res.json()["id"]
                return categoryID

# <----------------------------------------------->
# Sending a request to postman api to get all
# category indexes based on category name
# <----------------------------------------------->
def getCategoryIndexes(categoryName, dataObj):
        print("Getting categoryIndexes")
        categoryName.replace(" ", "%20")
        URL = "http://cd3tstapp.raben-group.com/api/global/categories/{}?call=getIndexesInfo&fetchValues=false&lang=pl".format(categoryName)
        
        headers = {
                "Cookie": dataObj.cookies,
                "Accept": "application/json",
                "Content-type": "application/json",
                "Authorization": dataObj.token
        }
        res = requests.get(URL, headers=headers)
        code = int(res.status_code)
        print("Status code: {}".format(code))

        if code == 200:
                for item in res.json():
                        indexName = item["name"]
                        indexID = item["id"]
                        dataObj.indexes[indexName] = indexID
        else:
                print(parseJson(res.text))

        return dataObj

# Helper functions (end)
# <----------------------------------------------->


# <----------------------------------------------->
# Convert request data from user to
# format required by Contman
# returns True if passed data is valid, False otherwise
# <----------------------------------------------->
def convertPendingToSending(json_data, dataObj):
        data = json_data
        categoryName = data["categoryName"]
        pendingCategoryIndexes = data["categoryIndexes"]
        documentClass = data["documentClass"]
        documentClass = documentClass.replace(" ", "%20")

        dataObj.documentClass = documentClass
        dataObj.categoryName = categoryName
        dataObj = getCategoryIndexes(categoryName, dataObj)

        # <----------------------------------------------->
        # Check if indexes are valid in this document class
        # <----------------------------------------------->
        for index in data["categoryIndexes"]:
            if index not in dataObj.indexes:
                return dataObj, False

        dataObj.outputFormat["categoryValues"][0].append(getCategoryID(categoryName, dataObj))
        
        outputIndexes = {}

        for index in pendingCategoryIndexes.keys():
                indexID = dataObj.indexes[index]
                outputIndexes[indexID] = pendingCategoryIndexes[index]
        
        dataObj.outputFormat["categoryValues"][0].append(outputIndexes)

        print("OUTPUT")
        pprint.pprint(dataObj.outputFormat)

        return dataObj, True
# <----------------------------------------------->
# Logging to contman
# <----------------------------------------------->
def login(dataObj):
        URL = "http://cd3tstapp.raben-group.com/api/login"
        body = {
                "domain":"-",
                "login":"-",
                "password":"-"
        }

        headers = {
                "Accept": "application/json",
                "Content-type": "application/json"
        }

        try:
                log("1. Login", debug)
                res = requests.post(URL, json = body, headers=headers)
                code = int(res.status_code)
                log("Status code: {}".format(code), debug)

                if code == 200:
                        resText = res.text
                        responseHeaders = res.headers
                        # <----------------------------------------------->
                        # Getting token to authorize next connections
                        # <----------------------------------------------->
                        token = res.json()["token"]

                        # <----------------------------------------------->
                        # storing cookies and token data to global object
                        # <----------------------------------------------->
                        dataObj.setCookies(responseHeaders["Set-Cookie"])
                        dataObj.setToken(token)
                        
                        return dataObj
                else:
                        print(res.text)

        except requests.exceptions.RequestException as error:
                raise SystemExit(error)

# <----------------------------------------------->
# Starting transaction
# <----------------------------------------------->
def startTransaction(dataObj):
        URL = "http://cd3tstapp.raben-group.com/api/avatar?call=startTransaction"

        headers = {
                "Cookie": dataObj.cookies,
                "Accept": "application/json",
                "Content-type": "application/json",
                "Authorization": dataObj.token
        }

        try:
                log("2. Start transaction", debug)

                res = requests.post(URL, headers=headers)
                code = int(res.status_code)

                log("Status code: {}".format(code), debug)

                if code == 200:
                        resText = res.text
                        responseHeaders = res.headers
                        # <----------------------------------------------->
                        # pretty print body of response and headers
                        # print(parseJson(resText), parseHeaders(responseHeaders), sep="\n------------------\n")
                        # <----------------------------------------------->
                        return dataObj
                else:
                        print(res.text)


        except requests.exceptions.RequestException as error:
                raise SystemExit(error)

# <----------------------------------------------->
# Creating document
# <----------------------------------------------->
def createDocument(dataObj):
        log("3. Create Document", debug)
        documentClass = dataObj.documentClass
        URL = "http://cd3tstapp.raben-group.com/api/global/classes/{}?call=create".format(documentClass)
        headers = {
                "Cookie": dataObj.cookies,
                "Accept": "application/json",
                "Content-type": "application/json",
                "Authorization": dataObj.token
        }

        body = dataObj.outputFormat

        try:
                res = requests.post(URL, json=body, headers=headers)
                code = int(res.status_code)

                if code == 200:
                        log("Done!", debug)
                        resText = res.text
                        responseHeaders = res.headers
                        # <----------------------------------------------->
                        # Getting document id from response
                        # to upload file in next request
                        # <----------------------------------------------->
                        dataObj.documentID = res.json()["id"]
                        return dataObj
                else:
                        print(res.text)

        except requests.exceptions.RequestException as error:
                raise SystemExit(error)

# <----------------------------------------------->
# Uploading file to the document
# <----------------------------------------------->
def uploadFile(dataObj):
        log("4. Upload file", debug)
        URL = "http://cd3tstapp.raben-group.com/api/services/documents/{}/files".format(dataObj.documentID)
        boundary = "testtest"
        headers = {
                "Cookie": dataObj.cookies,
                "Authorization": dataObj.token,
                "Accept": "*/*",
                "Content-type": "multipart/form-data; boundary={}".format(boundary)
        }

        # <----------------------------------------------->
        # Testing if example works
        # passing pdf file from directory
        # <----------------------------------------------->
        with open(os.path.join(sys.path[0], "api-cd3.pdf"), "rb") as file:
                dataFile = file.read()
                file.close()

        # <----------------------------------------------->
        # sending form data with boundary, name, filename
        # passing binary pdf data to send
        # <----------------------------------------------->
        input = ["--{}".format(boundary), 
                "Content-Disposition: form-data; name=\"plik5.pdf\"; filename=\"plik5.pdf\"",
                "Content-Type: application/pdf",
                str(dataFile.decode("latin-1")),
                "--{}--\r\n".format(boundary)]

        # <----------------------------------------------->
        # Joining body with enters
        # <----------------------------------------------->
        body = "\r\n".join(input)


        res = requests.post(URL, data=body, headers=headers)
        code = int(res.status_code)
        log("Status code: {}".format(code), debug)

        if code == 201:
                log("File uploaded!", debug)
                resText = res.text
                responseHeaders = res.headers
                # <----------------------------------------------->
                # pretty print of response and headers
                # print(parseJson(resText), parseHeaders(responseHeaders), sep="\n------------------\n")
                # <----------------------------------------------->
                return dataObj
        else:
                print(res.text)

# <----------------------------------------------->
# Commiting/finishing the transaction
# <----------------------------------------------->
def commitTransaction(dataObj):
        log("5. Commit Transaction", debug)
        URL = "http://cd3tstapp.raben-group.com/api/avatar?call=finishTransaction&commit=true"
        headers = {
                "Cookie": dataObj.cookies,
                "Accept": "application/json",
                "Content-type": "application/json",
                "Authorization": dataObj.token
        }
        res = requests.post(URL, headers=headers)
        code = int(res.status_code)

        log("Status code: {}".format(code), debug)

        if code == 200:
                log("Done!", debug)
        else:
                print(res.text)

        return dataObj

# <----------------------------------------------->
# Logging out
# <----------------------------------------------->
def logout(dataObj):
        log("6. Logout", debug)
        URL = "http://cd3tstapp.raben-group.com/api/avatar?call=logout"
        headers = {
                "Cookie": dataObj.cookies,
                "Accept": "application/json",
                "Content-type": "application/json",
                "Authorization": dataObj.token
        }
        res = requests.post(URL, headers=headers)
        code = int(res.status_code)

        log("Status code: {}".format(code), debug)

        if code == 200:
                log("Done!", debug)
        else:
                print(res.text)

        return dataObj
