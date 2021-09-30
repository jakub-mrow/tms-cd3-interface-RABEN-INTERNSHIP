import os 
import sys
import logging
from datetime import date
import subprocess

logging.basicConfig(
    filename="/app/monitor_logs/"+str(date.today()),
    filemode="a",
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p %Z",
    level=logging.INFO,
    encoding='utf-8'
)

print("RUNNING")

pid = str(os.getpid())
pidFile = "/app/monitor/tmp/pidcheck.pid"

if os.path.isfile(pidFile):
    logging.error("START OVERRIDE | Tried to start monitor again but it is still running!")
    sys.exit()

with open(pidFile, "w") as file:
    file.write(pid)

try:
    command = ["python", "/app/monitor/src/monitor.py"]
    subprocess.run(command)
finally:
    os.unlink(pidFile)