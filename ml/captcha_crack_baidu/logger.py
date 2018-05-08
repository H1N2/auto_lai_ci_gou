from datetime import datetime
import time


def log(msg):
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print('>> {0}: {1}'.format(t, msg))


if __name__ == '__main__':
    log('log A')
    time.sleep(2)
    log('log B')
