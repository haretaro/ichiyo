import chainer
from chainer import optimizers
import numpy as np
import csv
from net import Net

use_gpu = False
xp = cuda.cupy if use_gpu is True else np

x = []
y = []
f = open('testdata.csv','r')
data = csv.reader(f, delimiter=',')
for row in data:
    x.append(row[1])
    y.append(row[2])
model = Net(1,10)
optimizer = optimizers.Adam()
optimizer.setup(model)
optimizer.add_hook(chainer.optimizer.GradientClipping(grad_clip))
