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

buy_value = 0.1
sell_value = 0.9

loss_cut = 200 #損切り
profit_taking = 100 #利食い
deposit = 9e5 #証拠金
commission = 250 #手数料
buy_rate = 0.2 #一回の取引に使う金額の割合
init_money = 2e7 #所持金
stock = 0 #所持枚数
last_transit = 0
money = init_money #所持金
offset = 400 #予測が安定するまで取引を行わない
position = 'neutral' #sell, buy, neutral のどれかの状態を取る

end = 5 #終値の列
deviation = 7 #移動平均乖離率

xp = cuda.cupy if use_gpu is True else np
xp = np

#データ読み込み
in_data = []
data = []
f = open('nikkei5min.csv','r')
csvfile = csv.reader(f, delimiter=',')
for row in csvfile:
    if row[deviation] == '':
        continue
    data.append([row[i] for i in [end, deviation]])
data = np.asarray(data[-int(len(data) * 0.2):] , dtype=np.float32)
end_prices = data[:, 0]
in_data = data[:, 1:2]

in_data = xp.asarray(in_data, dtype=np.float32)

#モデルを読み込む
model = Net(1,20,1)
serializers.load_npz('ceiling_degree.model', model)

#ネットワークを試す関数
def evaluate(model, x):
    evaluator = model.copy()
    evaluator.reset_state()
    out = evaluator.predict(x)
    return chainer.cuda.to_cpu(out.data)

output = evaluate(model, in_data)
in_data = in_data
output = output

def buy(money, stock, current_price, last_transit, buy_rate = buy_rate, deposit = deposit, commission = commission):
    number_of_stock = min(money * buy_rate // current_price, money // deposit) - stock
    if number_of_stock < 0:
        number_of_stock = 0
    stock += number_of_stock
    money -= number_of_stock * current_price
    if number_of_stock != 0:
        money -= commission
        last_transit = current_price
        print('buy {},\tprice {},\tstock {},\tmoney {}, {}'.format(number_of_stock, current_price, stock,  money, position))
    return money, stock, last_transit

def sell(money, stock, current_price, last_transit, buy_rate = buy_rate, deposit = deposit, commission = commission):
    number_of_stock = min(money * buy_rate // current_price, money // deposit) + stock
    if number_of_stock < 0:
        number_of_stock = 0
    stock -= number_of_stock
    money += number_of_stock * current_price
    if number_of_stock != 0:
        money -= commission
        last_transit = current_price
        print('sell {},\tprice {},\tstock {},\tmoney {}, {}'.format(number_of_stock, current_price, stock,  money, position))
    return money, stock, last_transit

#シミュレーション
history = []
for current_price, ceiling_degree in zip(end_prices, output[offset:,0]):
    if position == 'neutral':
        if ceiling_degree < buy_value:
            money, stock, last_transit = buy(money, stock, current_price, last_transit)
            position = 'buy'

        elif ceiling_degree > sell_value:
            money, stock, last_transit = sell(money, stock, current_price, last_transit)
            position = 'sell'

    elif position == 'buy':
        if current_price > last_transit + profit_taking or current_price < last_transit - loss_cut:
            money, stock, last_transit = sell(money, stock, current_price, last_transit)
            position = 'neutral'

    elif position == 'sell':
        if current_price < last_transit - profit_taking or current_price > last_transit + loss_cut:
            money, stock, last_transit = buy(money, stock, current_price, last_transit)
            position = 'neutral'

    else:
        raise('positionに変な値入ってるエラー')
    history.append((stock, money))

#精算
if stock != 0:
    money += current_price * stock
    stock = 0
    history.append((stock, money))
    print('finaly, \tstock {0},\tmoney {1}, profit {2:,d} yen'.format(stock,  money, int(money - init_money)))

fig, ax1 = plt.subplots()
ax1.plot(end_prices[offset:], label='end_price')
plt.legend()
ax2 = ax1.twinx()
#ax2.plot(output[:,0], label='predicted_ceiling_degree', color='green')
ax2.plot([x[1] for x in history], label='money', color='green')
plt.grid()
plt.show()
