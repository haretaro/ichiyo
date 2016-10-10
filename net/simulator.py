#coding: utf-8
#モデルをロードするサンプル + ゴミシミュレータ

import chainer
from chainer import serializers, cuda
import csv
import numpy as np
import matplotlib.pyplot as plt
from net import Net

use_gpu = False
trade_price = 4 #次のタイムスパンでx円上がるなら買い, x円下がるなら売り
loss_cut = 400 #損切り
profit_taking = 1 #利食い #TODO: 手数料から計算する
deposit = 9e5 #証拠金
commission = 250 #手数料
buy_rate = 0.2 #一回の取引に使う金額の割合
init_money = 2e7 #所持金
stock = 0 #所持枚数
last_transit = 0
money = init_money #所持金
offset = 400 #予測が安定するまで取引を行わない

xp = cuda.cupy if use_gpu is True else np

#データ読み込み
in_data = []
f = open('nikkei5min.csv','r')
data = csv.reader(f, delimiter=',')
for row in data:
    in_data.append([row[i] for i in range(2,6)])
in_data = xp.asarray(in_data, dtype=np.float32)

#モデルを読み込む
model = Net(4,20,4)
serializers.load_npz('3M_epoch.model', model)

#ネットワークを試す関数
def evaluate(model, x):
    evaluator = model.copy()
    evaluator.reset_state()
    out = evaluator.predict(x)
    return chainer.cuda.to_cpu(out.data)

output = evaluate(model, in_data / 20000)
in_data = in_data
output = output * 20000
#output = in_data[1:]
#in_data = in_data[:-1]

def buy(money, stock, current_price, last_transit, buy_rate = buy_rate, deposit = deposit, commission = commission):
    number_of_stock = min(money * buy_rate // current_price, money // deposit) - stock
    if number_of_stock < 0:
        number_of_stock = 0
    stock += number_of_stock
    money -= number_of_stock * current_price
    if number_of_stock != 0:
        money -= commission
        last_transit = current_price
        print('buy {},\tprice {},\tstock {},\tmoney {}'.format(number_of_stock, current_price, stock,  money))
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
        print('sell {},\tprice {},\tstock {},\tmoney {}, {}'.format(number_of_stock, current_price, stock,  money, last_transit))
    return money, stock, last_transit

#シミュレーション
history = []
for current_price, prediction in zip(in_data[offset:,3], output[offset:]):

    ##損切り
    #if stock > 0 and current_price - last_transit < -loss_cut:
    #    money += stock * current_price
    #    stock = 0
    #    print('loss cut current{}, last{}, delta{}'.format(current_price, last_transit, current_price - last_transit))

    ##損切り
    #if stock < 0 and current_price - last_transit > loss_cut:
    #    money += stock * current_price
    #    stock = 0
    #    print('loss cut current{}, last{}'.format(current_price, last_transit))

    diff = prediction[3] - prediction[0]
    if diff > trade_price:
        #if stock == 0 or current_price - last_transit > profit_taking:
            money, stock, last_transit = buy(money, stock, current_price, last_transit)

    elif diff < trade_price:
        #if stock == 0 or last_transit - current_price > profit_taking:
            money, stock, last_transit = sell(money, stock, current_price, last_transit)
    history.append((stock, money))

#精算
if stock != 0:
    money += current_price * stock
    stock = 0
    history.append((stock, money))
    print('finaly, \tstock {0},\tmoney {1}, profit {2:,d} yen'.format(stock,  money, int(money - init_money)))

fig, ax1 = plt.subplots()
ax1.plot(in_data[:,0], label='in')
ax1.plot(output[:,0], label='prediction')
plt.legend()
ax2 = ax1.twinx()
ax2.plot([x[1] for x in history], label='money')
plt.title("money")
plt.grid()
plt.show()

plt.plot(output[:,0], label='start')
plt.plot(output[:,3], label='end')
plt.show()
