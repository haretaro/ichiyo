#coding: utf-8

import chainer
from chainer import serializers, cuda
import csv
import numpy as np
import matplotlib.pyplot as plt
from net import Net

use_gpu = False

xp = cuda.cupy if use_gpu is True else np

#データ読み込み
in_data = []
f = open('30minutes.csv','r')
data = csv.reader(f, delimiter=',')
for row in data:
    in_data.append(row[7])
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

plt.plot(in_data)
plt.plot(output)
plt.show()
