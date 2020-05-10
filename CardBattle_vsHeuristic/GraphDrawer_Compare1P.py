#coding: "utf-8"
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

Data1P = pd.read_csv("Model_EZero\Model1PRating.csv",header=None)
Data1P_DQN = pd.read_csv("Model\DQNModel1PRating.csv",header=None)


x1P = Data1P[0]
y1P = Data1P[1]
x1P_DQN = Data1P_DQN[0]
y1P_DQN = Data1P_DQN[1]

plt.xlabel("Games")
plt.ylabel("Rating")
plt.plot(x1P,y1P,label="1P")
plt.plot(x1P_DQN,y1P_DQN,label="1P_DQN")
plt.legend()
plt.show()
plt.savefig("Graph_Compare1P.png")

