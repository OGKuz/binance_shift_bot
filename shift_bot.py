import math
from binance_api import Binance
import config_trade
import statistics as st
import time
import requests

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


def take_info_hloc(API_KEY, API_SECRET, COIN, FRAME, Limit = 50) -> list:
    bot = Binance(API_KEY=API_KEY, API_SECRET=API_SECRET)
    try:
        data = bot.klines(
            symbol = COIN+'USDT',
            interval = FRAME,
            limit = Limit)
        hloc4 = list()
        for i in data:
            hloc4.append(st.mean((float(i[1]),float(i[2]),float(i[3]),float(i[4]))))
        return hloc4
    except Exception:
        return take_info_hloc(API_KEY=config_trade.API_KEY, API_SECRET=config_trade.API_SECRET, COIN=config_trade.COIN, FRAME=config_trade.FRAME, Limit = 50)


def put_order (side, price, quoteOrderQty, API_KEY, API_SECRET, COIN, type = 'LIMIT'):
    bot = Binance(API_KEY=API_KEY, API_SECRET=API_SECRET)
    def take_prec(COIN=COIN):
        prec = requests.get(f'https://api.binance.com/api/v3/exchangeInfo?symbol={COIN}USDT').json()
        return(float(prec['symbols'][0]['filters'][2]['stepSize']))
    print (quoteOrderQty)
    try:
        if side == 'BUY':
            quantity = round((quoteOrderQty/price) - ((quoteOrderQty/price)%take_prec()), 7)
            print (quantity)
        elif side == 'SELL':
            quantity = round(quoteOrderQty -  ((quoteOrderQty/price)%take_prec()), 7)
            print (quantity)
        '''a = bot.exchangeInfo()['symbols']
        for i in a:
            if i['symbol'] == 'BTCUSDT':
                print (i)'''
        return bot.createOrder(
            symbol=COIN+'USDT',
            side = side,
            type = type,
            quantity = quantity,
            price = round(price - price%0.01,2),
            recvWindow = 59999,
            timeInForce = 'GTC'
                )
    except Exception:
        print ('EROR EROR EROR ORDER PUT')
        return put_order (side, price, quoteOrderQty, type, API_KEY, API_SECRET, COIN)


def cancel_order (API_KEY, API_SECRET,COIN):  
    bot = Binance(API_KEY=API_KEY, API_SECRET=API_SECRET)
    try:
        return bot.cancelOrders(
            symbol = COIN+'USDT',
            recvWindow = 59999
        )
    except Exception:
        return cancel_order (API_KEY=config_trade.API_KEY, API_SECRET=config_trade.API_SECRET,COIN=config_trade.COIN)


def check_order (API_KEY, API_SECRET,COIN):
    bot = Binance(API_KEY=API_KEY, API_SECRET=API_SECRET)
    try:
        return bot.openOrders(
            symbol = COIN+'USDT',
            recvWindow = 59999
        )
    except Exception:
        check_order (API_KEY=config_trade.API_KEY, API_SECRET=config_trade.API_SECRET,COIN=config_trade.COIN)


def balance_check(API_KEY, API_SECRET):
    bot = Binance(API_KEY=API_KEY, API_SECRET=API_SECRET)
    try:
        balance = bot.account()
        return balance
    except:
        return balance_check(API_KEY=config_trade.API_KEY, API_SECRET=config_trade.API_SECRET,COIN=config_trade.COIN)


def main(API_KEY=config_trade.API_KEY, API_SECRET=config_trade.API_SECRET, COIN=config_trade.COIN, FRAME = config_trade.FRAME):
    while True:
        time_now = time.gmtime()[3:5]
        if time_now[0] == 0 and time_now[1] == 1:
            orders = check_order(API_KEY=API_KEY, API_SECRET=API_SECRET, COIN=COIN)
            print (orders)
            if len(orders) != 0:
                print(cancel_order(API_KEY=API_KEY, API_SECRET=API_SECRET, COIN=COIN))
            data = take_info_hloc(API_KEY=API_KEY, API_SECRET=API_SECRET, COIN=COIN, FRAME=FRAME, Limit=50)
            sma = SMA(data=data, period=3)[-1]
            shift = sma * config_trade.koef
            print (shift,sma)
            person_data_raw = balance_check(API_KEY=API_KEY, API_SECRET=API_SECRET)['balances']
            person_data = dict()
            for i in person_data_raw:
                if i['asset'] == f'{COIN}' or i['asset'] == 'USDT':
                    person_data[i['asset']] = i['free']
            print (person_data)
            if float(person_data[COIN])*sma < 12 and float(person_data['USDT']) > 12:
                if config_trade.quoteOrderQty:
                    put_order('BUY', shift, round(float(config_trade.quoteOrderQty)*0.98, 0), API_KEY=API_KEY, API_SECRET=API_SECRET, COIN=COIN, type='LIMIT')
                else:
                    put_order('BUY', shift, round(float(person_data['USDT'])*0.97, 0), API_KEY=API_KEY, API_SECRET=API_SECRET, COIN=COIN, type='LIMIT')
            if float(person_data[COIN])*sma > 12:
                put_order('SELL', sma, float(person_data[f'{COIN}']), type='LIMIT', API_KEY=API_KEY, API_SECRET=API_SECRET, COIN=COIN)
            else:
                pass
            time.sleep(60)
        else:
            orders = check_order(API_KEY=API_KEY, API_SECRET=API_SECRET, COIN=COIN)
            if len(orders) == 0:
                data = take_info_hloc(API_KEY=API_KEY, API_SECRET=API_SECRET, COIN=COIN, FRAME=FRAME, Limit=50)
                sma = SMA(data=data, period=3)[-1]
                shift = sma * config_trade.koef
                print (shift,sma)
                person_data_raw = balance_check(API_KEY=API_KEY, API_SECRET=API_SECRET)['balances']
                person_data = dict()
                for i in person_data_raw:
                    if i['asset'] == f'{COIN}' or i['asset'] == 'USDT':
                        person_data[i['asset']] = i['free']
                print (person_data)
                if float(person_data[COIN])*sma > 12:

                    put_order('SELL', sma, float(person_data[f'{COIN}']), type='LIMIT', API_KEY=API_KEY, API_SECRET=API_SECRET, COIN=COIN)

                elif float(person_data[COIN])*sma < 12 and float(person_data['USDT']) > 12:

                    if config_trade.quoteOrderQty:
                        put_order('BUY', shift, round(float(config_trade.quoteOrderQty)*0.98, 0), API_KEY=API_KEY, API_SECRET=API_SECRET, COIN=COIN, type='LIMIT')
                    else:
                        put_order('BUY', shift, round(float(person_data['USDT'])*0.97, 0), API_KEY=API_KEY, API_SECRET=API_SECRET, COIN=COIN, type='LIMIT')
                    
                else:
                    pass
                time.sleep(60)
            else:
                time.sleep(60)

        
if __name__ == '__main__':
    main()
    #print (check_order(API_KEY=config_trade.API_KEY, API_SECRET=config_trade.API_SECRET, COIN=config_trade.COIN))
    ...

