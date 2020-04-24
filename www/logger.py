
import logging
import os.path
from logging.handlers import TimedRotatingFileHandler

'''
Logging Levels
CRITICAL	50
ERROR	40
WARNING	30
INFO	20
DEBUG	10
NOTSET	0
'''

logfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log/picture.log')

#https://stackoverflow.com/questions/20240464/python-logging-file-is-not-working-when-using-logging-basicconfig
#logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(threadName)-10s %(message)s')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = TimedRotatingFileHandler(logfile, when="midnight", interval=1, encoding='utf-8')
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(threadName)-10s %(message)s'))
handler.suffix = "%Y%m%d"
logger.addHandler(handler)

PAGE = 4096
def tail(filepath, n=10):
    """
    实现 tail -n
    """
    res = ""
    with open(filepath, 'rb') as f:
        f_len = f.seek(0, 2)
        rem = f_len % PAGE
        page_n = f_len // PAGE
        r_len = rem if rem else PAGE
        while True:
            # 如果读取的页大小>=文件大小，直接读取数据输出
            if r_len >= f_len:
                f.seek(0)
                lines = f.readlines()[::-1]
                break

            f.seek(-r_len, 2)
            # print('f_len: {}, rem: {}, page_n: {}, r_len: {}'.format(f_len, rem, page_n, r_len))
            lines = f.readlines()[::-1]
            count = len(lines) -1   # 末行可能不完整，减一行，加大读取量

            if count >= n:  # 如果读取到的行数>=指定行数，则退出循环读取数据
                break
            else:   # 如果读取行数不够，载入更多的页大小读取数据
                r_len += PAGE
                page_n -= 1

    for line in lines[:n][::-1]:
        res += line.decode('utf-8')
    return res

def read_logs(lines=200):
    """
    获取最新的指定行数的 log
    :param lines: 最大的行数
    :returns: 最新指定行数的 log
    """

    if os.path.exists(logfile):
        return tail(logfile, lines)
    return ''