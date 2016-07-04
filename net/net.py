#coding: utf-8
#リカレントネット
import chainer
import chainer.functions as F
import chainer.links as L

class Net(chainer.Chain):
    #n_in 入力の次元数
    #n_units 中間層のノード数
    def __init__(self, n_in, n_units):
        super(Net, self).__init__(
                l_in = L.Linear(n_in, n_units),
                lstm1 = L.LSTM(n_units, n_units),
                lstm2 = L.LSTM(n_units, n_units),
                l_out = L.Linear(n_units, 1)
                )

    def __call__(self, x, t):
        return F.mean_squared_error(self.predict(x), t)

    def reset_state(self):
        self.lstm1.reset_state()
        self.lstm2.reset_state()

    def predict(self, x):
        h1 = F.sigmoid(self.l_in(x))
        h2 = self.lstm1(h1)
        h3 = self.lstm2(h2)
        y = self.l_out(h3)
        return y

class MoreLayersNet(chainer.Chain):
    #n_in 入力の次元数
    #n_units 中間層のノード数
    def __init__(self, n_in, n_units):
        super(MoreLayersNet, self).__init__(
                l_in = L.Linear(n_in, n_units),
                lstm1 = L.LSTM(n_units, n_units),
                l_hidden = L.Linear(n_units,n_units),
                l_out = L.Linear(n_units, 1)
                )

    def __call__(self, x, t):
        return F.mean_squared_error(self.predict(x), t)

    def reset_state(self):
        self.lstm1.reset_state()

    def predict(self, x):
        h1 = F.sigmoid(self.l_in(x))
        h2 = self.lstm1(h1)
        h3 = F.sigmoid(self.l_hidden(h2))
        y = self.l_out(h3)
        return y
