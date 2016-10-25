#coding: utf-8
#モデルをロードするサンプル + ゴミシミュレータ

import chainer
from chainer import serializers, cuda
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import sys
import math
sys.path.append('../net')
from net import Net
from datetime import datetime

validation_ratio = 0.8 #バリデーションに使う割合
test_ratio = 0.2 #テストデータに使う割合
if test_ratio + validation_ratio > 1:
    raise Exception('すまんがデータ使う割合は足して1以下になるようにしてくれ')

use_gpu = False
xp = cuda.cupy if use_gpu is True else np

deposit = 9e5 #証拠金
commission = 280 * 1.08 #手数料/枚 + 税
buy_rate = 0.2 #一回の取引に使う金額の割合
init_money = 2e7 #所持金
unit = 1000 #取引単位
offset = 0 #予測が安定するまで取引を行わない

csv_file_name = '../data/result_nikkei30min.csv'
model_file_name = '../models/5min_3M_epoch.model'

end = 5 #終値の列
deviation = 7 #移動平均乖離率
twitter = 10 #その日のツイート数
date = 0
time = 1


def buy(money, stock, current_price, last_transit, buy_rate, deposit, commission, show):
    number_of_stock = money * buy_rate // deposit - stock
    if number_of_stock < 0:
        number_of_stock = 0
    stock += number_of_stock
    if number_of_stock != 0:
        #money -= commission * number_of_stock
        last_transit = current_price
        if show:
            print('buy {},\tprice {}'.format(number_of_stock, current_price))
    return money, stock, last_transit

def sell(money, stock, current_price, last_transit, buy_rate, deposit, commission, show):
    number_of_stock = money * buy_rate // deposit + stock
    if number_of_stock < 0:
        number_of_stock = 0
    stock -= number_of_stock
    if number_of_stock != 0:
        #money -= commission * number_of_stock
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
    money -= commission * stock
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
dates = None

score_for_transaction = 0

#引数がパラメータのリストになったシミュレーション
#パラメータは買い閾値, 売り閾値, 損切り, 利食いのリスト
def simulateP(parameters, test=False, show=False, regularization=None, score_for_transaction=score_for_transaction):
    return simulate(parameters[0], parameters[1], parameters[2], parameters[3], test, show, regularization, score_for_transaction=score_for_transaction)
#シミュレーション
def simulate(buy_value, sell_value, loss_cut, profit_taking, test=False, show=False, regularization=None, score_for_transaction=score_for_transaction):
    global in_data
    global data
    global dates
    global output
    global end_prices

    money = init_money
    stock = 0 #所持枚数
    last_transit = 0
    position = 'neutral' #sell, buy, neutral のどれかの状態を取る
    state = 'neutral' #neutral, buying, sellingのどれか

#データ読み込み
    if in_data is None or test == True:
        in_data = []
        data = []
        raw_data = []
        dates = []
        dates_temp = []
        f = open(csv_file_name,'r')
        csvfile = csv.reader(f, delimiter=',')
        for row in csvfile:
            if row[deviation] == '':
                continue
            raw_data.append([row[i] for i in [end, deviation, twitter]])
            dates_temp.append(datetime.strptime(row[date] + ' ' + row[time], '%Y/%m/%d %H:%M:%S'))

        test_cut_point = int(len(raw_data) * test_ratio)
        validation_cut_point = int(len(raw_data) * (test_ratio + validation_ratio))

        data = np.asarray(raw_data[-validation_cut_point: -test_cut_point], dtype=np.float32)
        dates = dates_temp[-validation_cut_point: -test_cut_point]

        if test == True:
            data = np.asarray(raw_data[-test_cut_point:] , dtype=np.float32)
            dates = dates_temp[-test_cut_point:]

        end_prices = data[:, 0]
        in_data = data[:, 1:3]

        in_data = xp.asarray(in_data, dtype=np.float32)

#モデルを読み込む
        model = Net(2,20,1)
        serializers.load_npz(model_file_name, model)

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
            raise Exception('positionに変な値入ってるエラー')
        history.append((stock, money))

    if stock != 0:
        money, stock = payoff(money, stock, current_price, last_transit, buy_rate, deposit, commission, show)
        history.append((stock, money))

    def format_date(x, pos=None):
        N = len(dates)
        thisind = np.clip(int(x+0.5), 0, N-1)
        return dates[thisind].strftime('%Y/%m/%d')

    if show:
        print('finaly, \tstock {0},\tmoney {1}, profit {2:,d} yen'.format(stock,  money, int(money - init_money)))

    money_history = [init_money] + [h[1] for h in history]
    benefits = [a[0] - a[1] for a in zip(money_history[1:], money_history[:-1])]

    if regularization == 'log':
    #利益の対数を報酬にして大きな利益に鈍感にする
        benefits = [x + score_for_transaction if x != 0 else x for x in benefits]
        regularized = [math.log(a+1) if a >= 0 else -math.log(abs(a) +1) for a in benefits]
        return sum(regularized)

    s = [x + score_for_transaction if x != 0 else x for x in benefits]
    if show:
        number_of_transaction = sum(1 if x!=0 else 0 for x in benefits)
        number_of_win = sum(1 if x>1 else 0 for x in benefits)
        number_of_lose = sum(1 if x<0 else 0 for x in benefits)

        print(len(benefits))
        print('取引回数: {}'.format(number_of_transaction))
        print('勝率: {}'.format(number_of_win / number_of_transaction))

        ind = np.arange(len(end_prices))
        fig, ax1 = plt.subplots()
        ax1.plot(ind[offset:], end_prices[offset:], label='end_price')
        ax1.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
        ax1.set_ylabel('日経平均株価')
        #plt.legend()
        ax2 = ax1.twinx()
        ax2.plot([x[1] for x in history], label='money', color='green')
        ax2.set_ylabel('所持金')
        plt.grid()
        plt.show()
    return sum(s)

if __name__ == '__main__':
    #魔法の数字
    parameters = [0.4, 0.7, 30, 10] #底判定値、天井判定値、損切り、利食い
    parameters = [0.563349954, 0.7121350237, 44, 72]
    
    simulateP(parameters, False, True)
    simulateP(parameters, True, True)
