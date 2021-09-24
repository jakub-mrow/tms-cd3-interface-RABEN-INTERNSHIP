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

        fileTypes = folder["files"]

        for fileType in fileTypes:
            dataObj = Data()

            dataObj.folderPath = folder["path"]
            dataObj.categoryName = fileType["categoryName"]
            dataObj.documentClass = fileType["documentClass"]
            dataObj.indexesSetup = fileType["indexes"]
            dataObj.separator = fileType["separator"]
            dataObj.fileExtension = fileType["extension"]
            dataObj.wholeFileNameCat = fileType["wholeFileName"]

            dataObj.indexesSetup.append(dataObj.wholeFileNameCat)

            logging.info(f"Started adding files from folder: {dataObj.folderPath}")

            dataObj, check = func.dataCheck(dataObj, dataObj.folderPath)
            if check == False:
                continue

            filesCount = 0
            for file in os.listdir(dataObj.folderPath):
                if func.getExtension(file) == "."+dataObj.fileExtension:
                    dataObj.filePath = dataObj.folderPath+file
                    try:
                        dataObj.indexesValues = file.split(dataObj.separator)
                    except ValueError as error:
                        logging.info(f"Splitting the file name did not work | {error}")

                    dataObj.indexesValues.append(file)

                    dataObj.indexesOut = dict(zip(dataObj.indexesSetup, dataObj.indexesValues))

                    print(dataObj.indexesOut)

                    response, code = func.sendRequest(dataObj, URL)
                    if code == 201:
                        logging.info(f"{code} | {response}")
                        filesCount += 1
                        if os.path.exists(dataObj.filePath):
                            os.remove(dataObj.filePath)
                            logging.info(f"remove |{file} removed from directory: {dataObj.folderPath}")
                    else:
                        logging.error(f"{code} | {response}")

            logging.info(f"Added {filesCount} files with given format from folder {dataObj.folderPath}")

# <----------------------------------------------->
# Runnning main function 
# <----------------------------------------------->
if __name__ == "__main__":
    main()