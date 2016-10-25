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
import matplotlib.ticker as ticker
from datetime import datetime

csv_file = '../data/result_nikkei5min.csv'
model_file = '../models/5min_3M_epoch.model'
end = 5 #終値の列
deviation = 7 #移動平均乖離率
twitter = 10
use_gpu = False
xp = cuda.cupy if use_gpu is True else np

#データ読み込み
with open(csv_file,'r') as f:
    csvf = csv.reader(f, delimiter=',')
    raw_data = []
    for row in csvf:
        if row[deviation] == '':
            continue
        raw_data.append([row[i] for i in range(11)]) #10列目まで読み込む

    end_prices = [[x[end]] for x in raw_data]
    dates = [datetime.strptime(x[0] + ' ' + row[1], '%Y/%m/%d %H:%M:%S') for x in raw_data]
    in_data = [[x[deviation], x[twitter]] for x in raw_data]
    in_data = xp.asarray(in_data, dtype=np.float32)

def evaluate(model, x):
    evaluator = model.copy()
    evaluator.reset_state()
    out = evaluator.predict(x)
    return chainer.cuda.to_cpu(out.data)

def format_date(x, pos=None):
    N = len(dates)
    thisind = np.clip(int(x+0.5), 0, N-1)
    return dates[thisind].strftime('%Y/%m/%d')

#モデルを読み込む
model = Net(2,20,1)
serializers.load_npz(model_file, model)

output = evaluate(model, in_data)

fig, ax1 = plt.subplots()
ax1.plot([x[end] for x in raw_data])
ax1.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
ax2 = ax1.twinx()
ax2.plot(output, color='green')
plt.show()

#予測天井度を、読み込んだデータにくっつける
output_data = [x[0] + x[1] for x in zip(raw_data, output.tolist())]


writer = csv.writer(open('output.csv','w'), delimiter=',')
for row in output_data:
    writer.writerow(row)

print('made output.csv')
