# main.py
# dependencies: requests, ptyz, python-dateutil
import datetime
import threading
import requests
import time
import pytz
from dateutil import parser
from datetime import datetime as _datetime

from session import Session
from reservation import Reservation
from configs import COOKIE, SHOP_REF, SHOP_NAME, SCHEDULE_LIST, DATE, TIME # TARGET_TS REMOVED


def run(clients, schedule):
    print(f'[예약 시작]: {schedule["day"]} {schedule["time"]}')
    reservation = Reservation(
        session=clients,
        shop_ref=SHOP_REF,
        shop_alias=SHOP_NAME,
        day=schedule["day"],
        time=schedule["time"],
    )
    count = 0
    
    try:
        while True:
            resp2 = reservation.get_resp2(schedule["encrypted"])
            if resp2 is not None:
                break
            elif count > 20:
                break
            time.sleep(0.1)
            count += 1
        
        if resp2 is None:
            raise Exception("Empty resp2")
        
        token = reservation.prepare(resp2)
        result = reservation.reserve(token, resp2)
        print(f'[result]: {result}')
    except Exception as e:
        print(f'[Error]: {e}')


def start_reservation():
    clients = Session(COOKIE)
    for schedule in SCHEDULE_LIST:
        threading.Thread(target=run, args=(clients, schedule,)).start()


def main():
    while True:
        response = requests.get('https://app.catchtable.co.kr')
        date = response.headers["Date"]
        server_ts = int(parser.parse(date).timestamp())  # 캐치테이블 서버 시간
        tz = pytz.timezone('Asia/Seoul')
        dt = DATE + TIME
        dt_obj = datetime.datetime.strptime(str(dt), '%Y%m%d%H%M%S')
        dt_with_tz = tz.localize(dt_obj, is_dst=None)
        target_ts = int((dt_with_tz - _datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds())
        diff = target_ts - server_ts
        print(f'{diff}초 남음')
        if diff >= 1:
            time.sleep(diff/2)
        else:
            break
    
    start_reservation()


if __name__ == "__main__":
    main()
