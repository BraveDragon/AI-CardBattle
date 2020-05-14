#coding: "utf-8"
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

Data1P = pd.read_csv("Model_EZero\EZeroWinRate.csv",header=None)
Data2P = pd.read_csv("Model_EZero\EZeroWinRate_2P.csv",header=None)


x1P = Data1P[0]
y1P = Data1P[1]
x2P = Data2P[0]
y2P = Data2P[1]


plt.xlabel("Games÷100")
plt.ylabel("WinRate")
plt.plot(x1P,y1P,label="1P")
plt.plot(x2P,y2P,label="2P")
plt.legend()
plt.show()
plt.savefig("Graph_WinRate.png")

