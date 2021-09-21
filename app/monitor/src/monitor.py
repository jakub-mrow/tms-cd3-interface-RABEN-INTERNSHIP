from data import Data
from datetime import date
import os
import requests
import logging
import monitor_func as func
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

if __name__ == "__main__":
    directory = "/chfakt2"
    for file in os.listdir(directory):
        path = os.path.abspath(directory+"/"+file)
        response, code = func.sendRequest(URL, path)
        if code == 201:
            logging.info(f"{code} | {response}")
        else:
            logging.error(f"{code} | {response}")

"""
    folders = []
    for folder in folders:
        logID = str(uuid.uuid4())
        dataObj = Data()
        "/chfakt2/tms/RDE/prod/epod2/"

        dataObj, check = func.dataCheck(dataObj, logID)
        if check == False:
            continue
        logging.info("Data loaded successfully")
        for filename in os.listdir(path):
            filePath = ""
            response, code = func.sendRequest(filePath, URL)
            if code == 201:
                logging.info(f"{code} | {response}")
            else:
                logging.error(f"{code} | {response}")
        
"""