#coding: utf-8
#リカレントネット
import chainer
import chainer.functions as F
import chainer.links as L

class Net(chainer.Chain):
    #n_in 入力の次元数
    #n_units 中間層のノード数
    def __init__(self, n_in, n_units, n_out):
        super(Net, self).__init__(
                l1 = L.Linear(n_in, n_units),
                l2 = L.LSTM(n_units, n_units),
                l3 = L.Linear(n_units, n_out)
                )

    def __call__(self, x, t):
        return F.mean_squared_error(self.predict(x), t)

    def reset_state(self):
        self.l2.reset_state()

    def predict(self, x):
        h1 = F.sigmoid(self.l1(x))
        h2 = self.l2(h1)
        y = self.l3(h2)
        return y

class MLP(chainer.Chain):
    def __init__(self, n_in, n_units):
        super(MLP, self).__init__(
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

    def reset_state(self):
        return None
