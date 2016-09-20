#coding: utf-8
#モデルをロードするサンプル + ゴミシミュレータ

import chainer
from chainer import serializers, cuda
import csv
import numpy as np
import matplotlib.pyplot as plt
from net import Net

use_gpu = False
buy_price = 10 #次のタイムスパンでx円上がるなら買い
sell_price = 10
deposit = 9e5 #証拠金
commission = 250 #手数料
buy_rate = 0.8 #一回の取引に使う金額の割合
money = 2e7 #所持金
stock = 0 #所持枚数

xp = cuda.cupy if use_gpu is True else np

#データ読み込み
in_data = []
f = open('30minutes.csv','r')
data = csv.reader(f, delimiter=',')
for row in data:
    in_data.append(row[1])
in_data = np.asarray(in_data, dtype=np.float32)

#モデルを読み込む
model = Net(1,20)
serializers.load_npz('my.model', model)


#ネットワークを試す関数
def evaluate(model, x):
    evaluator = model.copy()
    evaluator.reset_state()
    out = evaluator.predict(chainer.Variable(xp.asarray([[x_] for x_ in x])))
    return chainer.cuda.to_cpu(out.data)

output = evaluate(model, in_data)

def buy(money, stock, current_price, buy_rate = buy_rate, deposit = deposit, commission = commission):
    number_of_stock = min(money * buy_rate // current_price, money // deposit) - stock
    if number_of_stock < 0:
        number_of_stock = 0
    stock += number_of_stock
    money -= number_of_stock * current_price
    money -= commission
    print('buy {},\tprice {},\tstock {},\tmoney {}'.format(number_of_stock, current_price, stock,  money))
    return money, stock

def sell(money, stock, current_price, buy_rate = buy_rate, deposit = deposit, commission = commission):
    number_of_stock = min(money * buy_rate // current_price, money // deposit) + stock
    if number_of_stock < 0:
        number_of_stock = 0
    stock -= number_of_stock
    money += number_of_stock * current_price
    money -= commission
    print('sell {},\tprice {},\tstock {},\tmoney {}'.format(number_of_stock, current_price, stock,  money))
    return money, stock

history = []
for current_price, prediction in zip(in_data[:-1], output):
    diff = current_price - prediction
    if diff < buy_price:
        money, stock = buy(money, stock, current_price)
    elif diff > sell_price:
        money, stock = sell(money, stock, current_price)
    history.append((stock, money))

plt.plot(in_data)
plt.plot(output)
plt.show()
plt.plot([x[1] for x in history])
plt.show()
