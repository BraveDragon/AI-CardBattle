#coding: "utf-8"
import chainer
import chainer.functions as F
import chainer.links as L
import chainerrl

Inputs = 23
Outputs = 5
Hidden_Channels = 64

class DQN(chainer.Chain):

    def __init__(self, obs_size=Inputs, n_actions=Outputs, n_hidden_channels=Hidden_Channels):
        super(DQN, self).__init__()
        with self.init_scope():
            self.l0 = L.Linear(obs_size, n_hidden_channels).to_gpu(0)
            self.l1 = L.Linear(n_hidden_channels, n_hidden_channels).to_gpu(0)
            self.out = L.Linear(n_hidden_channels, n_actions).to_gpu(0)
    
    def forward(self, x):
        h = F.rrelu(self.l0(x))
        h = F.rrelu(self.l1(h))
        h = self.out(h)

        return h