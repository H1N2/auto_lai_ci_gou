import schedule
import time

from tasks import buy2

if __name__ == '__main__':
    # 下面任务为串行执行，如需并行需用多线程对任务再次封装
    schedule.every().days.at("00:45").do(buy2)

    while True:
        schedule.run_pending()
        time.sleep(1)
