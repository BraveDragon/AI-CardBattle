#coding: "utf-8"
import torch.nn as nn
import torch.nn.functional as F

Inputs = 1920
Outputs = 5
#学習に使用するモデル
Model = nn.Sequential(
                    nn.Linear(in_features=Inputs,out_features=64),
                    nn.LeakyReLU(),
                    nn.Linear(in_features=64,out_features=64),
                    nn.LeakyReLU(),
                    nn.Linear(in_features=64,out_features=Outputs)
                    )