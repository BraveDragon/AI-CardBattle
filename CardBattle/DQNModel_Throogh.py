#coding: "utf-8"
import torch.nn as nn
import torch.nn.functional as F

Inputs = 1920
Outputs = 5

class DQN(nn.Module):

    def __init__(self, states, outputs):
        super(DQN, self).__init__()
        self.states = states
        self.outputs = outputs
        self.fc = nn.Sequential(
            nn.Linear(self.states, 64),
            nn.LeakyReLU(),
            nn.Linear(64,64),
            nn.LeakyReLU(),
            nn.Linear(64,self.outputs)
        )
    
    def forward(self,x):
        x = self.fc(x.view(-1, self.states))
        return x


