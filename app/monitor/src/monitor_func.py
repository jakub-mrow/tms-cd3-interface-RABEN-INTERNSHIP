import requests
import contman_conn as cont
import logging
import json
import os
from datetime import date

logging.basicConfig(
    filename="app/monitor_logs/"+str(date.today()),
    filemode="a",
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
    encoding='utf-8'
)

def dataCheck(dataObj, logID):
    categoryName = dataObj.categoryName

    dataObj, loginError = cont.login(dataObj)
    if loginError is not None:
        logging.error("{} | {} | {}".format(logID, "login", loginError["request-error"]))
        return dataObj, False

    dataObj, indexCheck = cont.getCategoryIndexes(categoryName, dataObj)
    if indexCheck is not None:
        logging.error("{} | {} | {}".format(logID, "index-check", indexCheck["request-error"]))
        return dataObj, False

    dataObj, logoutError = cont.logout(dataObj)
    if logoutError is not None:
        logging.error("{} | {} | {}".format(logID, "logout", logoutError["request-error"]))
        return dataObj, False

    logging.info("{} | {} ".format(logID, "Data succefully checked!"))
    return dataObj, True


def sendRequest(URL, filePath):
    body = {
    "documentClass": "Dokumenty EDNTMP",
    "categoryName": "TMS Invoices",
    "categoryIndexes": {
        "ABCD": "PL12",
        "ENV": "NONE",
        "Depot": "0000",
        "Nr faktury": "TSTINVOICE-43-API-JAKUB",
        "Nazwa pliku": os.path.basename(filePath),
        "Nr kontrahenta": "CUSTOMERID",
        "Typ dokumentu": "3",
        "Nazwa pliku": os.path.basename(filePath),
        "TMS Invoices - nazwa pliku": os.path.basename(filePath) 
    },
    "filePath": filePath
}

    auth=("test", "test2")

    try:
        res = requests.post(URL, json=body, auth=auth)
        code = int(res.status_code)
        data = res.text
        print(data)
        return data, code

    except requests.exceptions.RequestException as error:
        return {"request-error": error}, 404

def loadSettings(settings):
    with open(settings) as set:
        data = json.load(set)
        