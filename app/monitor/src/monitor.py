from data import Data
from datetime import date
import os
import time
import requests
import logging
import monitor_func as func
import json
import uuid

logging.basicConfig(
    filename="/app/monitor_logs/"+str(date.today()),
    filemode="a",
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p %Z",
    level=logging.INFO,
    encoding='utf-8'
)

URL = "http://api:5000/documents"

REFRESHKEY = "REFRESH_MONITOR_TIME"
REFRESH_TIME = int(os.getenv(REFRESHKEY))


def main():

    while True:
        with open("/app/monitor/config/settings.json") as set:
            data = json.load(set)
        folders = data["array"]

        logging.info("Starting the monitor")

        for folder in folders:
            if os.path.isdir(folder["path"]):

                fileTypes = folder["files"]

                for fileType in fileTypes:
                    dataObj = Data()

                    dataObj.folderPath = folder["path"]
                    dataObj.categoryName = fileType["categoryName"]
                    dataObj.documentClass = fileType["documentClass"]
                    dataObj.indexesSetup = fileType["indexes"]
                    dataObj.separator = fileType["separator"]
                    dataObj.fileExtension = fileType["extension"]
                    dataObj.delete = fileType["delete"]

                    if "wholeFileName" in fileType:
                        dataObj.wholeFileNameCat = fileType["wholeFileName"]
                        dataObj.indexesSetup.append(dataObj.wholeFileNameCat)

                    logging.info(f"Started adding files from folder: {dataObj.folderPath} with extension: {dataObj.fileExtension}")

                    dataObj, check = func.dataCheck(dataObj, dataObj.folderPath)
                    if check == False:
                        continue

                    filesCount = 0
                    for file in os.listdir(dataObj.folderPath):
                        if func.getExtension(file) == "."+dataObj.fileExtension:
                            dataObj.filePath = dataObj.folderPath+file
                            dataObj.fileName = file

                            noExtensionFileName = os.path.splitext(file)[0]
                            try:
                                dataObj.indexesValues = noExtensionFileName.split(dataObj.separator)
                            except ValueError as error:
                                logging.info(f"Splitting the file name did not work | {error}")

                            if "wholeFileName" in fileType:
                                dataObj.indexesValues.append(file)

                            dataObj.indexesOut = dict(zip(dataObj.indexesSetup, dataObj.indexesValues))

                            print(dataObj.indexesOut)

                            response, code = func.sendRequest(dataObj, URL)
                            if code == 201:
                                logging.info(f"{code} | {response}")
                                filesCount += 1
                                if os.path.exists(dataObj.filePath) and dataObj.delete == True:
                                    os.remove(dataObj.filePath)
                                    logging.info(f"remove |{file} removed from directory: {dataObj.folderPath}")
                            else:
                                logging.error(f"{code} | {response}")

                    logging.info(f"Added {filesCount} files with given format from folder {dataObj.folderPath}")

            else:
                logging.error("Directory does not exist")

        time.sleep(REFRESH_TIME)

# <----------------------------------------------->
# Runnning main function 
# <----------------------------------------------->
if __name__ == "__main__":
    main()