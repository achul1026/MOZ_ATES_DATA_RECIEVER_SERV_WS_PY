import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


def get_logger():
    # 로그 파일 및 콘솔 핸들러 생성
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # 로그 파일 및 콘솔 핸들러 생성
    # console_handler = logging.StreamHandler()
    # console_handler.setLevel(logging.DEBUG)
    # console_handler.setFormatter(formatter)

    # 로그 파일 핸들러 설정
    log_dir = "logs"
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    log_file_handler = TimedRotatingFileHandler(filename=log_dir+'/app.log', when='midnight', interval=1, backupCount=7)
    log_file_handler.setFormatter(formatter)
    log_file_handler.setLevel(logging.DEBUG)

    # 루트 로거에 핸들러 추가
    logger = logging.getLogger()
    # logger.addHandler(console_handler)
    logger.addHandler(log_file_handler)

    return logger
