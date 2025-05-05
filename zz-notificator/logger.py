import threading
from datetime import datetime
import pathlib
import traceback
import os
import sys
from parameters import Parameters

send_SMS = True
rootPath = str(pathlib.Path(__file__).parent.absolute())

class Logger:
    CRITICAL = 0
    NORMAL = 1
    RICH = 2
    FULL = 3

    phone = None

    def __init__(self, filename="main", verbosity=NORMAL):
        self.filename = filename
        self._terminate = False
        self.queue = []
        self.verbosity = verbosity

    def log(self, txt, _verbosity=NORMAL):
        if _verbosity > self.verbosity:
            return
        print(str(txt))

        dateStr = datetime.now().strftime('%Y-%m-%d')
        datetimeStr = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        path = f"/var/log/zz-notificator/{dateStr}"
        if not os.path.exists(path):
            os.makedirs(path)

        with open(f"{path}/{self.filename}.log", "a") as file:
            file.write(datetimeStr + " >> " + str(txt) + "\n")

    def log_exception(self, e):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        self.log(str(e))
        self.log(str(exc_type) + " : " + str(fname) + " : " + str(exc_tb.tb_lineno))

        #self.log(traceback.format_exc())

        # exc_type, exc_obj, exc_tb = sys.exc_info()
        # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        # Log(str(e))
        # Log(str(exc_type) +" : "+ str(fname) + " : " +str(exc_tb.tb_lineno))

    def terminate(self):
        self._terminate = True
