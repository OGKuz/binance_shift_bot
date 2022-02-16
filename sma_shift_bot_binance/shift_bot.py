import math
from binance_api import Binance
import config_trade
import statistics as st
import time


def SMA(data, period):
    if len(data) == 0:
        raise Exception("Empty data")
    if period <= 0:
        raise Exception("Invalid period")

    interm = 0
    result = []
    nan_inp = 0
    
    for i, v in enumerate(data):
        if math.isnan(data[i]):
            result.append(math.nan)
            interm = 0
            nan_inp += 1
        else:
            interm += v
            if (i+1 - nan_inp) < period:
                result.append(math.nan)
            else:
                result.append(interm/float(period))
                if not math.isnan(data[i+1-period]):
                    interm -= data[i+1-period]
    return result


def take_info_hloc(API_KEY=config_trade.API_KEY, API_SECRET=config_trade.API_SECRET, COIN=config_trade.COIN, FRAME=config_trade.FRAME, Limit = 50) -> list:
    bot = Binance(API_KEY=API_KEY, API_SECRET=API_SECRET)
    try:
        data = bot.klines(
            symbol = COIN,
            interval = FRAME,
            limit = Limit)
        hloc4 = list()
        for i in data:
            hloc4.append(st.mean((float(i[1]),float(i[2]),float(i[3]),float(i[4]))))
        return hloc4
    except Exception:
        return take_info_hloc(API_KEY=config_trade.API_KEY, API_SECRET=config_trade.API_SECRET, COIN=config_trade.COIN, FRAME=config_trade.FRAME, Limit = 50)


def put_order (side, price, quoteOrderQty = config_trade.quoteOrderQty, type = 'LIMIT', API_KEY=config_trade.API_KEY, API_SECRET=config_trade.API_SECRET,COIN=config_trade.COIN):
    bot = Binance(API_KEY=API_KEY, API_SECRET=API_SECRET)
    try:
        return bot.createOrder(
            symbol=COIN,
            side = side,
            type = type,
            quoteOrderQty = quoteOrderQty,
            price = price,
            recvWindow = 59999,
            timeInForce = 'GTC'
            )
    except Exception:
        return put_order (side, price, quoteOrderQty = config_trade.quoteOrderQty, type = 'limit', API_KEY=config_trade.API_KEY, API_SECRET=config_trade.API_SECRET,COIN=config_trade.COIN)


def cancel_order (API_KEY=config_trade.API_KEY, API_SECRET=config_trade.API_SECRET,COIN=config_trade.COIN):  
    bot = Binance(API_KEY=API_KEY, API_SECRET=API_SECRET)
    try:
        return bot.cancelOrder(
            symbol = COIN,
            recvWindow = 59999
        )
    except Exception:
        cancel_order (API_KEY=config_trade.API_KEY, API_SECRET=config_trade.API_SECRET,COIN=config_trade.COIN)


def check_order (API_KEY=config_trade.API_KEY, API_SECRET=config_trade.API_SECRET,COIN=config_trade.COIN):
    bot = Binance(API_KEY=API_KEY, API_SECRET=API_SECRET)
    try:
        return bot.openOrders(
            symbol = COIN,
            recvWindow = 59999
        )
    except Exception:
        check_order (API_KEY=config_trade.API_KEY, API_SECRET=config_trade.API_SECRET,COIN=config_trade.COIN)


if __name__ == '__main__':
    sma = SMA(take_info_hloc(),3)
    shift_sma = list(map(lambda x: x*config_trade.koef,sma))
    cancel_order()
    put_order('BUY', int(shift_sma[-1]))
    count = config_trade.quoteOrderQty/shift_sma[-1]*0.999
    while True:
        if time.gmtime()[3:5] == (0,0):
            sma = SMA(take_info_hloc(),3)
            shift_sma = list(map(lambda x: x*config_trade.koef,sma))
            cancel_order()
            put_order('BUY', int(shift_sma[-1]))
            count = config_trade.quoteOrderQty/shift_sma[-1]
            time.sleep (60)
        elif check_order() == False:
            sma = SMA(take_info_hloc(),3)
            put_order('SELL', int(sma[-1]), quoteOrderQty=int((count*sma[-1])))
            while check_order() != False:
                sma = SMA(take_info_hloc(),3)
                cancel_order()
                put_order('SELL', int(sma[-1]), quoteOrderQty=int((count*sma[-1])))
                time.sleep(60)
            sma = SMA(take_info_hloc(),3)
            shift_sma = list(map(lambda x: x*config_trade.koef,sma))
            put_order('BUY', int(shift_sma[-1]))
            count = config_trade.quoteOrderQty/shift_sma[-1]*0.999       
        else:
            time.sleep(60)
    

