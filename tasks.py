import schedule
import time
import traceback

from shelf import Shelf
from breed import Breed
from sale import Sale
from buy import Buy
from cfg import COOKIE as cookie
from ml.captcha_crack_baidu.logger import log


def sale():
    log('启动卖出定时任务')
    sale = Sale(cookie)
    try:
        sale.sale_all(100, 0)
        sale.sale_all(100, 1)
    except:
        traceback.print_exc()
    log('卖出定时任务执行完成')


def shelf():
    log('启动挂出繁育定时任务')
    shelf = Shelf(cookie)
    try:
        # shelf.shelf_all(100, 0)
        # shelf.shelf_all(100, 1)
        # shelf.shelf_all(100, 2)
        rare_degree_price_dic = {0: 100, 1: 100, 2: 100, 3: 1000, 4: 100000, 5: 1000000}
        shelf.shelf_all_once(rare_degree_price_dic)
    except:
        traceback.print_exc()
    log('挂出繁育定时任务执行完成')


def breed():
    log('启动内部繁育定时任务')
    breed = Breed(cookie)
    breed.breed_until_max_trade_times(2)
    log('内部繁育定时任务执行完成')


def buy1():
    log('启动购买定时任务')
    buy = Buy(cookie)
    # 购买卓越狗 价格不高于200
    # buy.buy_angel_pets_until_max_trade_times(200)
    # 购买卓越狗 价格不高于160， 代数不高于2代，数量不超过10条
    buy.buy_pets_until_max_trade_times(160, 2, 2, 10)
    # 购买史诗狗 价格不高于2500， 代数不高于3代，数量不超过2条
    # buy.buy_pets_until_max_trade_times(2500, 3, 3, 5)
    log('购买定时任务执行完成')


def buy2():
    log('启动购买定时任务')
    buy = Buy(cookie)
    # 购买卓越狗 价格不高于200
    # buy.buy_angel_pets_until_max_trade_times(200)
    # 购买卓越狗 价格不高于160， 代数不高于2代，数量不超过10条
    # buy.buy_pets_until_max_trade_times(160, 2, 2, 10)
    # 购买史诗狗 价格不高于2500， 代数不高于3代，数量不超过5条
    buy.buy_pets_until_max_trade_times(2500, 3, 3, 5)
    log('购买定时任务执行完成')


if __name__ == '__main__':
    # 下面任务为串行执行，如需并行需用多线程对任务再次封装
    schedule.every().hours.do(sale)
    schedule.every().hours.do(shelf)
    schedule.every().days.at("00:01").do(breed)
    schedule.every().days.at("00:01").do(buy1)

    while True:
        schedule.run_pending()
        time.sleep(1)
