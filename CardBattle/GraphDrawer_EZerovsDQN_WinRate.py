#coding: "utf-8"
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

Data1P_DQN = pd.read_csv("Model_EZero\EZeroWinRate.csv",header=None)
Data2P_DQN = pd.read_csv("Model\DQNWinRate_2P.csv",header=None)

x1P_DQN = Data1P_DQN[0]
y1P_DQN = Data1P_DQN[1]
x2P_DQN = Data2P_DQN[0]
y2P_DQN = Data2P_DQN[1]

plt.xlabel("Games÷100")
plt.ylabel("WinRate")

plt.plot(x1P_DQN,y1P_DQN,label="1P (ε-zero)")
plt.plot(x2P_DQN,y2P_DQN,label="2P (DQN)")
plt.legend()
plt.show()
plt.savefig("WinRate_EZerovsDQN.png")
