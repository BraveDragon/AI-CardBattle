#coding: "utf-8"
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

Data2P = pd.read_csv("Model_EZero\Model2PRating.csv",header=None)
Data2P_DQN = pd.read_csv("Model\DQNModel2PRating.csv",header=None)


x2P = Data2P[0]
y2P = Data2P[1]
x2P_DQN = Data2P_DQN[0]
y2P_DQN = Data2P_DQN[1]

plt.xlabel("Games")
plt.ylabel("Rating")
plt.plot(x2P,y2P,label="2P")
plt.plot(x2P_DQN,y2P_DQN,label="2P_DQN")
plt.legend()
plt.show()
plt.savefig("Graph_Compare2P.png")

