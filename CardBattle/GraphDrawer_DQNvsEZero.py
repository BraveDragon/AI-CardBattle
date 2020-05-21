#coding: "utf-8"
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

Data1P = pd.read_csv("Model\DQNModel1PRating.csv",header=None)
Data2P = pd.read_csv("Model_EZero\Model2PRating.csv",header=None)


x1P = Data1P[0]
y1P = Data1P[1]
x2P = Data2P[0]
y2P = Data2P[1]


plt.xlabel("Games")
plt.ylabel("Rating")
plt.plot(x1P,y1P,label="1P (DQN)")
plt.plot(x2P,y2P,label="2P (ε-zero)")
plt.legend()
plt.show()
plt.savefig("Graph_DQNvsEZero.png")

