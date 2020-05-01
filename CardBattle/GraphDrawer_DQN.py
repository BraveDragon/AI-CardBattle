#coding: "utf-8"
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

Data1P_DQN = pd.read_csv("Model\DQNModel1PRating.csv",header=None)
Data2P_DQN = pd.read_csv("Model\DQNModel2PRating.csv",header=None)

x1P_DQN = Data1P_DQN[0]
y1P_DQN = Data1P_DQN[1]
x2P_DQN = Data2P_DQN[0]
y2P_DQN = Data2P_DQN[1]

plt.xlabel("Games")
plt.ylabel("Rating")

plt.plot(x1P_DQN,y1P_DQN,label="1P_DQN")
plt.plot(x2P_DQN,y2P_DQN,label="2P_DQN")
plt.legend()
plt.show()
plt.savefig("Graph_DQN.png")
