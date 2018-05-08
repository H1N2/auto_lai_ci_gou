import schedule
import time

from tasks import breed

if __name__ == '__main__':
    # 下面任务为串行执行，如需并行需用多线程对任务再次封装
    schedule.every().days.at("00:43").do(breed)

    while True:
        schedule.run_pending()
        time.sleep(1)
