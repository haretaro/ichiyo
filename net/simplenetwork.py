import chainer
from chainer import optimizers, cuda
import chainer.functions as F
import chainer.links as L
import numpy as np
import csv
import math
import matplotlib.pyplot as plt

n_epoch = 20 #エポック
batchsize = 100 #バッチサイズ
bprop_len = 100 #何回でバックプロパゲーションを打ち切るか(trancate)
n_units = 200 #中間層のユニット数
grad_clip = 5 #誤差関数の絶対値をこの値に制限する
use_gpu = True #GPUを使うかどうか

xp = cuda.cupy if use_gpu is True else np

train_data_x = []
train_data_y = []
f = open('30minutes.csv','r')
data = csv.reader(f, delimiter=',')
for row in data:
    train_data_x.append(row[7])
    train_data_y.append(row[7])
raw_data = np.asarray(train_data_x, dtype=np.float32)
train_data_x = raw_data[:-1]
train_data_y = raw_data[1:]

plt.plot(train_data_x)
plt.plot(train_data_y)

plt.show()

class Net(chainer.Chain):
    def __init__(self, n_in, n_units):
        super(Net, self).__init__(
                l1 = L.Linear(n_in, n_units),
                l2 = L.Linear(n_units, n_units),
                l3 = L.Linear(n_units, 1)
                )

    def __call__(self, x, t):
        return F.mean_squared_error(self.predict(x), t)

    def predict(self, x):
        h1 = F.sigmoid(self.l1(x))
        h2 = F.sigmoid(self.l2(h1))
        y = self.l3(h2)
        return y

model = Net(1, n_units)
if use_gpu is True:
    model.to_gpu()

optimizer = optimizers.Adam()
optimizer.setup(model)
loss = []
sum_loss = 0
length = len(train_data_x)
batch_idxs = list(range(batchsize))
for epoch in range(1, n_epoch + 1):
    sum_loss = 0.0
    for i in range(0, length, batchsize):
        x = chainer.Variable(xp.asarray([[x] for x in train_data_x[i: i+batchsize]]))
        t = chainer.Variable(xp.asarray([[t] for t in train_data_y[i: i+batchsize]]))
        model.zerograds()
        loss_data = model(x, t)
        sum_loss += loss_data.data
        loss_data.backward()
        optimizer.update()
    loss.append(sum_loss / length)
    if epoch % 10 ==0:
        print('epoch {}, error {}'.format(epoch, sum_loss / length))

#plt.plot(loss)
#plt.show()

#ネットワークを試す関数
def evaluate(model, x):
    output = []
    evaluator = model.copy()
    for i in range(len(x)):
        t = evaluator.predict(chainer.Variable(xp.asarray([[x[i]]])))
        output.append(t.data[0])
    return output

output = evaluate(model, train_data_x)
plt.plot(output[:200])
plt.plot(train_data_y[:200])
plt.show()
