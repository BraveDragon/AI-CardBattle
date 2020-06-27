#coding: "utf-8"
import random
from collections import deque

#ReplayMemory用のクラス
class ReplayMemory(object):
    def __init__(self, capacity):
        self.memory = deque(maxlen=capacity)
        
    def load(self, experience):
        self.memory.append(experience)
    
    def sample(self,batch_size):
        ReturnSample = []
        for i in range(batch_size):
            ReturnSample.extend(random.sample(self.memory, 1))

        return ReturnSample

    def length(self):
        return len(self.memory)