import requests
import contman_conn as cont
import logging
import json
import os
import base64
from datetime import date

logging.basicConfig(
    filename="app/monitor_logs/"+str(date.today()),
    filemode="a",
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
    encoding='utf-8'
)

def dataCheck(dataObj, folderName):
    categoryName = dataObj.categoryName

    dataObj, loginError = cont.login(dataObj)
    if loginError is not None:
        logging.error("{} | {}".format("login", loginError["request-error"]))
        return dataObj, False

    dataObj, documentClassCheck = cont.getDocumentClassID(dataObj.documentClass, dataObj)
    if documentClassCheck is not None:
        logging.error("{} | {}".format("documentClass-check", documentClassCheck["request-error"]))
        return dataObj, False

    dataObj, categoryCheck = cont.getCategoryID(dataObj.categoryName, dataObj)
    if categoryCheck is not None:
        logging.error("{} | {}".format("category-check", categoryCheck["request-error"]))
        return dataObj, False

    dataObj, indexCheck = cont.getCategoryIndexes(categoryName, dataObj)
    if indexCheck is not None:
        logging.error("{} | {}".format("index-check", indexCheck["request-error"]))
        return dataObj, False

    dataObj, logoutError = cont.logout(dataObj)
    if logoutError is not None:
        logging.error("{} | {}".format("logout", logoutError["request-error"]))
        return dataObj, False

    logging.info("{} | {} ".format("Data succefully checked!", folderName))
    return dataObj, True


def sendRequest(dataObj, URL):
    print(dataObj.filePath)
    with open(dataObj.filePath, "rb") as file:
        dataFile = file.read()
        fileBase64 = str(base64.b64encode(dataFile).decode("utf-8"))
        file.close()

    body = {
    "documentClass": dataObj.documentClass,
    "categoryName": dataObj.categoryName,
    "categoryIndexes": dataObj.indexesOut,
    "fileName": dataObj.fileName,
    "base64": fileBase64
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

def getExtension(fileName):
    return os.path.splitext(fileName)[1]
        