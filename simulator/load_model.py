#coding: utf-8
#モデルをロードして予測結果をcsvに書き込む

import chainer
from chainer import serializers, cuda
import sys
sys.path.append('../net')
from net import Net
import csv
import numpy as np
import matplotlib.pyplot as plt
import chainer.functions as F

csv_file = '../data/result_nikkei30min.csv'
model_file = '../models/30min_3M_epoch.model'
end = 5 #終値の列
deviation = 7 #移動平均乖離率
twitter = 10
ceiling_degree = 9
use_gpu = False
xp = cuda.cupy if use_gpu is True else np

#データ読み込み
with open(csv_file,'r') as f:
    csvf = csv.reader(f, delimiter=',')
    raw_data = []
    for row in csvf:
        if row[deviation] == '' or row[ceiling_degree] == '':
            continue
        raw_data.append([row[i] for i in range(11)]) #10列目まで読み込む

    end_prices = [[x[end]] for x in raw_data]
    in_data = [[x[deviation], x[twitter]] for x in raw_data]
    in_data = xp.asarray(in_data, dtype=np.float32)
    target = [[x[ceiling_degree]] for x in raw_data]
    target = xp.asarray(target, dtype=np.float32)

def evaluate(model, x, y):
    evaluator = model.copy()
    evaluator.reset_state()
    out = evaluator.predict(x)
    error = F.mean_squared_error(out, y)
    return chainer.cuda.to_cpu(out.data), error.data

#モデルを読み込む
model = Net(2,20,1)
serializers.load_npz(model_file, model)

output, error = evaluate(model, in_data[:int(len(in_data) * 0.8)], target[:int(len(target) * 0.8)])
print('error {}'.format(error))
output, error = evaluate(model, in_data[-int(len(in_data) * 0.2):], target[-int(len(target) * 0.2):])
print('test error {}'.format(error))

output, error = evaluate(model, in_data, target)

fig, ax1 = plt.subplots()
ax1.plot([x[end] for x in raw_data])
ax2 = ax1.twinx()
ax2.plot(output, color='green')
plt.show()
