import base64
from datetime import datetime
from logging import LoggerAdapter

import logging
from pathlib import Path
import signal
from typing import List
import asyncio
import websockets
import json

from sqlalchemy import text

import db
from _logger import logger
from db import MozCameraEnfOrgFile, MozCameraEnfOrg

if __name__ == "__main__":
    session = db.open_session()
    verity_db_connection = session.execute(text("SELECT 1 from dual"))
    logging.info(f"DB connection verified : {verity_db_connection.fetchone()[0]}")

with open('settings.json') as conf_j:
    config = json.load(conf_j)
app_config = config['app']


def gen_fail_data(vlt):
    date_str = datetime.now().strftime('%Y%m%d')
    tme_str = datetime.now().strftime('%H%M%S')
    name = f"{vlt['data'].get('code','NoneCode')}_{vlt['data'].get('car_plate','NoneCarPlate')}_{tme_str}.json"

    json_string = json.dumps(vlt)
    _dir = "vlt_fails" + '/' + date_str
    Path(_dir).mkdir(parents=True, exist_ok=True)
    path_name = Path(_dir + '/' + name)
    with open(path_name, 'w') as file:
        file.write(json_string)
    file.close()


def save_b64_image(root, name: str, b64_data) -> str:
    image64 = base64.b64decode(b64_data)
    date_str = datetime.now().strftime('%Y%m%d')
    _dir = (root if root+"/" else "")+"vlt_img" + '/' + date_str

    Path(_dir).mkdir(parents=True, exist_ok=True)
    path_name = Path(_dir + '/' + name)
    logging.info(f"path={path_name}")
    jpg = open(path_name, 'wb')
    jpg.write(image64)
    jpg.close()
    return str(path_name)


def save_vlt_images(vlt, images: List, cnt, org_idx) -> List[str]:
    file_list: List[str] = []
    session = db.open_session()
    try:
        for idx, b64_data in enumerate(images):
            # 폴더에 이미지 저장
            name = f"{cnt}_{vlt['avg_speed']}_{vlt['enforce_code']}_{idx}.jpg"
            filepath = save_b64_image(app_config['file_path'], name, b64_data)
            new_file_info = MozCameraEnfOrgFile(
                org_idx=org_idx,
                seq=idx,
                file_path=filepath
            )
            session.add(new_file_info)
            file_list.append(filepath)
            session.flush()
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    return file_list


async def handle_vlt_message(vlt_message):
    vlt = vlt_message['data']
    logging.info(f"code {vlt['code']}, time={vlt['enforce_time']}")
    session = db.open_session()
    # 삽입할 데이터 생성
    new_info = MozCameraEnfOrg(
        code=vlt['code'],
        enforce_lane=vlt['enforce_lane'],
        avg_speed=vlt['avg_speed'],
        enforce_speed=vlt['enforce_speed'],
        signal_system=vlt['signal_system'],
        signal_info=vlt['signal_info'],
        enforce_mode=vlt['enforce_mode'],
        time=vlt['time'],
        addr=vlt['addr'],
        enforce_time=vlt['enforce_time'],
        car_plate=vlt['car_plate'],
        enforce_code=vlt['enforce_code'],
        speed_limit=vlt['speed_limit'],
        cr_dt=datetime.now()
    )
    session.add(new_info)
    session.flush()
    idx = new_info.idx
    if len(vlt['img_data']) > 0:
        try:
            await save_vlt_images(vlt, vlt['img_data'], idx, idx)
            logging.info(f"Inserted org : {idx}")
        except Exception as e:
            session.rollback()
            raise
    session.commit()


async def handler_for_vlt(websocket):
    logging.info("/ws/vlt/ connected")
    cnt = 0

    while True:
        message = await websocket.recv()
        json_data = json.loads(message)
        """data format
            {
                'code': 'H1647',
                'enforce_lane': 3, 'avg_speed': 65, 'enforce_speed': 1, 'signal_system': 1, 'signal_info': 0,
                'enforce_mode': 1, 'time': 0, 'addr': '서해안고속도로_상행_시점_2', 'enforce_time': '2022-01-27T11:20:25',
                'car_plate': '경기98사6682', 'enforce_code': 1, 'speed_limit': 65,
                'img_data': [bs64chars, bs64chars, ...]
            }
        """
        try:
            await handle_vlt_message(json_data)
        except Exception as e:
            gen_fail_data(json_data)
            logging.error(e)


async def handler(websocket):
    if websocket.path == "/ws/vlt/":
        await handler_for_vlt(websocket)
    else:
        # No handler for this path; close the connection.
        return


svr = websockets.serve(handler, "localhost", logger=LoggerAdapter(logger, None),
                       port=app_config["port"])
loop = asyncio.get_event_loop()

loop.add_signal_handler(signal.SIGINT, loop.stop)
loop.add_signal_handler(signal.SIGTERM, loop.stop)  # kill -15 pid
loop.run_until_complete(svr)
loop.run_forever()
