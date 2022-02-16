from binance_api import Binance
import statistics as st
import shift_bot, time, config_test


def test_shiftsma (coin, frame, multiply):
    bot = Binance('','')


    data = bot.klines(
        symbol = coin,
        interval = frame,
        limit = 1000)
    hloc4 = list()
    high = list()
    low = list()
    deals = list()


    for i in data:
        hloc4.append(st.mean((float(i[1]),float(i[2]),float(i[3]),float(i[4]))))
        low.append(float(i[3]))
        high.append(float(i[2]))



    sma = shift_bot.SMA(hloc4,3)
    shift_sma=list(map(lambda x: x*multiply, sma))


    start = 0
    for i in enumerate(shift_sma):

        if low[i[0]] <= i[1] and start == 0:
            start = i[1]
            continue
        
        if start != 0:
            if high[i[0]] >= sma[i[0]]:
                deals.append((sma[i[0]]/start-1))
                start = 0
                continue

        
    
    finish = 1
    for i in deals:
        finish = finish * (1+i)
    

    return f'{finish*100}%, count deals:{len(deals)}'

if __name__ == '__main__':

    print (test_shiftsma (coin=config_test.coin, frame=config_test.frame, multiply=config_test.multiply))
    time.sleep(120)