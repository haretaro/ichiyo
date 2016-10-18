#coding: utf-8
#モデルをロードするサンプル + ゴミシミュレータ

import chainer
from chainer import serializers, cuda
import csv
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append('../net')
from net import Net

use_gpu = False

def buy(money, stock, current_price, last_transit, buy_rate, deposit, commission, show):
    number_of_stock = min(money * buy_rate // current_price, money // deposit) - stock
    if number_of_stock < 0:
        number_of_stock = 0
    stock += number_of_stock
    if number_of_stock != 0:
        money -= commission
        last_transit = current_price
        if show:
            print('buy {},\tprice {}'.format(number_of_stock, current_price))
    return money, stock, last_transit

def sell(money, stock, current_price, last_transit, buy_rate, deposit, commission, show):
    number_of_stock = min(money * buy_rate // current_price, money // deposit) + stock
    if number_of_stock < 0:
        number_of_stock = 0
    stock -= number_of_stock
    if number_of_stock != 0:
        money -= commission
        last_transit = current_price
        if show:
            print('sell {},\tprice {}'.format(number_of_stock, current_price))
    return money, stock, last_transit

#精算
def payoff(money, stock, current_price, last_transit, buy_rate, deposit, commission, show=True):
    benefit = (current_price - last_transit) * stock * unit
    if show:
        print('stock {}, current{}, last{}, benefit {}'.format(stock, current_price, last_transit, benefit))
    money += benefit
    money -= commission
    stock = 0
    return money, stock

#ネットワークを試す関数
def evaluate(model, x):
    evaluator = model.copy()
    evaluator.reset_state()
    out = evaluator.predict(x)
    return chainer.cuda.to_cpu(out.data)

in_data = None
data = None
output = None

#引数がパラメータのリストになったシミュレーション
#パラメータは買い閾値, 売り閾値, 損切り, 利食いのリスト
def simulateP(parameters, test=False, show=False):
    return simulate(parameters[0], parameters[1], parameters[2], parameters[3], test, show)
#シミュレーション
def simulate(buy_value, sell_value, loss_cut, profit_taking, test=True, show=True):
    global in_data
    global data
    global output
    global end_prices

    deposit = 9e5 #証拠金
    commission = 250 #手数料
    buy_rate = 0.2 #一回の取引に使う金額の割合
    init_money = 2e7 #所持金
    global unit
    unit = 1000 #取引単位
    stock = 0 #所持枚数
    last_transit = 0
    money = init_money #所持金
    offset = 100 #予測が安定するまで取引を行わない
    position = 'neutral' #sell, buy, neutral のどれかの状態を取る
    state = 'neutral' #neutral, buying, sellingのどれか

    end = 5 #終値の列
    deviation = 7 #移動平均乖離率

    xp = cuda.cupy if use_gpu is True else np
    xp = np

#データ読み込み
    if in_data is None or in_data is None or test == True:
        in_data = []
        data = []
        f = open('../data/nikkei5min.csv','r')
        csvfile = csv.reader(f, delimiter=',')
        for row in csvfile:
            if row[deviation] == '':
                continue
            data.append([row[i] for i in [end, deviation]])

        data = np.asarray(data[-int(len(data) * 0.2): -int(len(data) * 0.1)], dtype=np.float32)
        if test == True:
            data = np.asarray(data[-int(len(data) * 0.1):] , dtype=np.float32)
        end_prices = data[:, 0]
        in_data = data[:, 1:2]

        in_data = xp.asarray(in_data, dtype=np.float32)

#モデルを読み込む
        model = Net(1,20,1)
        serializers.load_npz('ceiling_degree.model', model)

        output = evaluate(model, in_data)
        in_data = in_data
        output = output


#シミュレーション
    history = []
    for current_price, ceiling_degree in zip(end_prices, output[offset:,0]):
        if position == 'neutral':
            if state == 'neutral':
                if ceiling_degree < buy_value:
                    state = 'buying'
                elif ceiling_degree > sell_value:
                    state = 'selling'
            elif state == 'buying':
                if ceiling_degree > buy_value:
                    money, stock, last_transit = buy(money, stock, current_price, last_transit, buy_rate, deposit, commission, show)
                    if stock > 0:
                        position = 'buy'
            elif state == 'selling':
                if ceiling_degree < sell_value:
                    money, stock, last_transit = sell(money, stock, current_price, last_transit, buy_rate, deposit, commission, show)
                    if stock < 0:
                        position = 'sell'

        elif position == 'buy':
            if current_price > last_transit + profit_taking or current_price < last_transit - loss_cut:
                money, stock = payoff(money, stock, current_price, last_transit, buy_rate, deposit, commission, show)
                position = 'neutral'
                state = 'neutral'

        elif position == 'sell':
            if current_price < last_transit - profit_taking or current_price > last_transit + loss_cut:
                money, stock = payoff(money, stock, current_price, last_transit, buy_rate, deposit, commission, show)
                position = 'neutral'
                state = 'neutral'

        else:
            raise('positionに変な値入ってるエラー')
        history.append((stock, money))

    if stock != 0:
        money, stock = payoff(money, stock, current_price, last_transit, buy_rate, deposit, commission, show)
        history.append((stock, money))

    if show:
        print('finaly, \tstock {0},\tmoney {1}, profit {2:,d} yen'.format(stock,  money, int(money - init_money)))

        fig, ax1 = plt.subplots()
        ax1.plot(end_prices[offset:], label='end_price')
        plt.legend()
        ax2 = ax1.twinx()
        ax2.plot([x[1] for x in history], label='money', color='green')
        plt.grid()
        plt.show()
    return money - init_money


if __name__ == '__main__':
    #魔法の数字
    parameters = [0.37582741900938954, 0.30106857718840624, 826, 89]
    simulateP(parameters, True, True)
