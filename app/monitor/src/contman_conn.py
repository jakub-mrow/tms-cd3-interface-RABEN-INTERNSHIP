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

        try:
                res = requests.get(URL, headers=headers)
                code = int(res.status_code)
                log("Status code: {}".format(code))

                if code == 200:
                        for item in res.json():
                                indexName = item["name"]
                                indexID = item["id"]
                                dataObj.indexes[indexName] = indexID
                        return dataObj, None
                else:
                        log(parseJson(res.text))
                        return dataObj, {"request-error": [code, res.text]}

        except requests.exceptions.RequestException as error:
                return dataObj, {"request-error": error}



# Helper functions (end)
# <----------------------------------------------->

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
                        return dataObj, {"request-error": [code, res.text]}

        except requests.exceptions.RequestException as error:
                return dataObj, {"request-error": error}

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
                        return dataObj, {"request-error": [code, res.text]}
        except requests.exceptions.RequestException as error:
                return dataObj, {"request-error": error}

        return dataObj, None