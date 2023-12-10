import logging

def initLogger():
    # 设置日志器的级别
    logger = logging.getLogger('detector_logger')
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = initLogger()

