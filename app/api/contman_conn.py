import requests
import json
from data import Data
import pprint
import os
import sys
import uuid

global debug
global urlValue
global passValue
global loginValue
global domainValue

# <----------------------------------------------->
# DEBUG MODE
# If you want to see prints, set variable debug to True,
# if False nothing will be shown
#
# If there is an error in a response,
# body of the reponse will always be printed
# <----------------------------------------------->
debug = True
def log(message):
        if debug == True:
                print(message)


urlKey = "CD3URL"
urlValue = os.getenv(urlKey)
loginKey = "CD3LOGIN"
loginValue = os.getenv(loginKey)
passKey = "CD3PASSWORD"
passValue = os.getenv(passKey)
domainKey = "CD3DOMAIN"
domainValue = os.getenv(domainKey)

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
# document class ID based on class name, if it doesnt
# exist, function returns error
# <----------------------------------------------->
def getDocumentClassID(className, dataObj):
        log("Getting classDocumentID")
        className.replace(" ", "%20")
        URL = urlValue+"global/classes/{}".format(className)
        headers = {
                "Cookie": dataObj.cookies,
                "Accept": "application/json",
                "Content-type": "application/json",
                "Authorization": dataObj.token
        }

        try:
                res = requests.get(URL, headers=headers)
                code = int(res.status_code)
                log("Status code: {}".format(code))

                if code == 200:
                        categoryName = res.json()["id"]
                        return categoryName
                else:
                        return {"error": "This document class does not exist. Check the request body!"}
        except requests.exceptions.RequestException as error:
                return {"request-error": error}

# <----------------------------------------------->
# Sending a request to postman api to search for
# categoryID based on category name
# <----------------------------------------------->
def getCategoryID(categoryName, dataObj):
        log("Getting categoryDocumentID")
        categoryName.replace(" ", "%20")
        URL = urlValue+"global/categories/{}".format(categoryName)
        headers = {
                "Cookie": dataObj.cookies,
                "Accept": "application/json",
                "Content-type": "application/json",
                "Authorization": dataObj.token
        }
        res = requests.get(URL, headers=headers)
        code = int(res.status_code)
        log("Status code: {}".format(code))

        if code == 200:
                categoryID = res.json()["id"]
                return categoryID

# <----------------------------------------------->
# Sending a request to postman api to get all
# category indexes based on category name
# <----------------------------------------------->
def getCategoryIndexes(categoryName, dataObj):
        log("Getting categoryIndexes")
        categoryName.replace(" ", "%20")
        URL = urlValue+"global/categories/{}?call=getIndexesInfo&fetchValues=false&lang=pl".format(categoryName)
        
        headers = {
                "Cookie": dataObj.cookies,
                "Accept": "application/json",
                "Content-type": "application/json",
                "Authorization": dataObj.token
        }
        res = requests.get(URL, headers=headers)
        code = int(res.status_code)
        log("Status code: {}".format(code))

        if code == 200:
                for item in res.json():
                        indexName = item["name"]
                        indexID = item["id"]
                        dataObj.indexes[indexName] = indexID
        else:
                log(parseJson(res.text))

        return dataObj

# Helper functions (end)
# <----------------------------------------------->


# <----------------------------------------------->
# Convert request data from user to
# format required by Contman
# returns True if passed data is valid, False otherwise
# <----------------------------------------------->
def convertFormat(json_data, dataObj):
        data = json_data
        categoryName = data["categoryName"]
        pendingCategoryIndexes = data["categoryIndexes"]
        documentClass = data["documentClass"]
        documentClass = documentClass.replace(" ", "%20")

        dataObj.filePath = data["filePath"]
        dataObj.fileName = os.path.basename(dataObj.filePath)
        dataObj.fileExtension = os.path.splitext(data["filePath"])[1]

        if dataObj.fileExtension == ".pdf":
                dataObj.mimetype = "application/pdf"
        if dataObj.fileExtension == "docx":
                dataObj.mimetype = "application/msword"
        if dataObj.fileExtension == "xlsx":
                dataObj.mimetype = "application/vnd.ms-excel"

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

        log("OUTPUT")
        pprint.pprint(dataObj.outputFormat)

        return dataObj, True
# <----------------------------------------------->
# Logging to contman
# <----------------------------------------------->
def login(dataObj):
        URL = urlValue+"login"
        body = {
                "domain":domainValue,
                "login":loginValue,
                "password":passValue
        }

        headers = {
                "Accept": "application/json",
                "Content-type": "application/json"
        }

        try:
                log("1. Login")
                res = requests.post(URL, json = body, headers=headers)
                code = int(res.status_code)
                log("Status code: {}".format(code))

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
                        
                        return dataObj, None
                else:
                        log(res.text)
                        return {"request-error": [code, res.text]}

        except requests.exceptions.RequestException as error:
                return dataObj, {"request-error": error}

# <----------------------------------------------->
# Starting transaction
# <----------------------------------------------->
def startTransaction(dataObj):
        URL = urlValue+"avatar?call=startTransaction"

        headers = {
                "Cookie": dataObj.cookies,
                "Accept": "application/json",
                "Content-type": "application/json",
                "Authorization": dataObj.token
        }

        try:
                log("2. Start transaction")

                res = requests.post(URL, headers=headers)
                code = int(res.status_code)

                log("Status code: {}".format(code))

                if code == 200:
                        resText = res.text
                        responseHeaders = res.headers
                        # <----------------------------------------------->
                        # pretty print body of response and headers
                        # print(parseJson(resText), parseHeaders(responseHeaders), sep="\n------------------\n")
                        # <----------------------------------------------->
                        return dataObj, None
                else:
                        log(res.text)
                        return {"request-error": [code, res.text]}

        except requests.exceptions.RequestException as error:
                return dataObj, {"request-error": error}

# <----------------------------------------------->
# Creating document
# <----------------------------------------------->
def createDocument(dataObj):
        log("3. Create Document")
        documentClass = dataObj.documentClass
        URL = urlValue+"global/classes/{}?call=create".format(documentClass)
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
                        log("Done!")
                        resText = res.text
                        responseHeaders = res.headers
                        # <----------------------------------------------->
                        # Getting document id from response
                        # to upload file in next request
                        # <----------------------------------------------->
                        dataObj.documentID = res.json()["id"]
                        return dataObj, None
                else:
                        log(res.text)
                        return {"request-error": [code, res.text]}

        except requests.exceptions.RequestException as error:
                return dataObj, {"request-error": error}

# <----------------------------------------------->
# Uploading file to the document
# <----------------------------------------------->
def uploadFile(dataObj):
        log("4. Upload file")
        URL = urlValue+"services/documents/{}/files".format(dataObj.documentID)
        # generate random string of characters for boundary
        boundary = str(uuid.uuid4())
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
                "Content-Disposition: form-data; name=\"{}\"; filename=\"{}\"".format("plik20.pdf", "plik20.pdf"),
                "Content-Type: application/pdf",
                str(dataFile.decode("latin-1")),
                "--{}--\r\n".format(boundary)]

        # <----------------------------------------------->
        # Joining body with enters
        # <----------------------------------------------->
        body = "\r\n".join(input)

        try:
                res = requests.post(URL, data=body, headers=headers)
                code = int(res.status_code)
                log("Status code: {}".format(code))

                if code == 201:
                        log("File uploaded!")
                        resText = res.text
                        responseHeaders = res.headers
                        # <----------------------------------------------->
                        # pretty print of response and headers
                        # print(parseJson(resText), parseHeaders(responseHeaders), sep="\n------------------\n")
                        # <----------------------------------------------->
                        return dataObj, None
                else:
                        log(res.text)
                        return {"request-error": [code, res.text]}

        except requests.exceptions.RequestException as error:
                return dataObj, {"request-error": error}

# <----------------------------------------------->
# Commiting/finishing the transaction
# <----------------------------------------------->
def commitTransaction(dataObj):
        log("5. Commit Transaction")
        URL = urlValue+"avatar?call=finishTransaction&commit=true"
        headers = {
                "Cookie": dataObj.cookies,
                "Accept": "application/json",
                "Content-type": "application/json",
                "Authorization": dataObj.token
        }
        try:
                res = requests.post(URL, headers=headers)
                code = int(res.status_code)

                log("Status code: {}".format(code))

                if code == 200:
                        log("Done!")
                else:
                        log(res.text)
                        return {"request-error": [code, res.text]}
        except requests.exceptions.RequestException as error:
                return dataObj, {"request-error": error}

        return dataObj, None

# <----------------------------------------------->
# Logging out
# <----------------------------------------------->
def logout(dataObj):
        log("6. Logout")
        URL = urlValue+"avatar?call=logout"
        headers = {
                "Cookie": dataObj.cookies,
                "Accept": "application/json",
                "Content-type": "application/json",
                "Authorization": dataObj.token
        }
        res = requests.post(URL, headers=headers)
        code = int(res.status_code)

        log("Status code: {}".format(code))

        try:
                if code == 200:
                        log("Done!")
                else:
                        log(res.text)
                        return {"request-error": [code, res.text]}
        except requests.exceptions.RequestException as error:
                return dataObj, {"request-error": error}

        return dataObj, None
