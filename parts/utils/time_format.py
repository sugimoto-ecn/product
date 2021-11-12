import time
from datetime import datetime , timedelta

def current_time_format():
        local_time = datetime.today()
        today = datetime.today()
        # ymd = time.strftime("%Y.%m.%d (%a)", time.gmtime())
        ymd = datetime.strftime(today , "%Y %m/%d (%a)")
        hms = local_time.strftime("%H:%M:%S")
        return {
            "ymd":ymd,
            "hms":hms
        }