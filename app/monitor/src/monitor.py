from data import Data
from datetime import date
import os
import requests
import logging
import monitor_func as func
import json
import uuid

logging.basicConfig(
    filename="app/monitor_logs/"+str(date.today()),
    filemode="a",
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
    encoding='utf-8'
)

URL = "http://api:5000/documents"

def main():
    with open("/app/monitor/config/settings.json") as set:
        data = json.load(set)
    folders = data["array"]

    logging.info("Starting the monitor")

    for folder in folders:
        dataObj = Data()

        dataObj.folderPath = folder["path"]
        dataObj.categoryName = folder["files"]["categoryName"]
        dataObj.documentClass = folder["files"]["documentClass"]
        dataObj.indexesSetup = folder["files"]["indexes"]
        dataObj.separator = folder["files"]["separator"]
        dataObj.fileExtension = folder["files"]["extension"]

        logging.info(f"Started adding files from folder: {dataObj.folderPath}")

        dataObj, check = func.dataCheck(dataObj, dataObj.folderPath)
        if check == False:
            continue

        for file in os.listdir(dataObj.folderPath):
            if func.getExtension(file) == "."+dataObj.fileExtension:
                dataObj.filePath = dataObj.folderPath+file
                try:
                    dataObj.indexesValues = file.split(dataObj.separator)
                except ValueError as error:
                    logging.info(f"Splitting the file name did not work | {error}")

                dataObj.indexesOut = dict(zip(dataObj.indexesSetup, dataObj.indexesValues))

                print(dataObj.indexesOut)

                response, code = func.sendRequest(dataObj, URL)
                if code == 201:
                    logging.info(f"{code} | {response}")
                else:
                    logging.error(f"{code} | {response}")

        logging.info(f"Added files with given format from folder {dataObj.folderPath}")

# <----------------------------------------------->
# Runnning main function 
# <----------------------------------------------->
if __name__ == "__main__":
    main()