#coding: "utf-8"
#このソースコードは以下のサイトを参考に作成
# Reinforcement Learning (DQN) Tutorial — PyTorch Tutorials 1.4.0 documentation
# URL : https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html
from mlagents_envs.environment import UnityEnvironment
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision.transforms as T
import numpy as np
from collections import deque
from collections import namedtuple
import random

#必要なクラス等を定義
#ReplayMemory用のクラス
class ReplayMemory(object):
    def __init__(self, capacity):
        self.memory = deque(maxlen=capacity)
        
    def load(self, experience):
        self.memory.append(experience)
    
    def sample(self,batch_size):
        return random.sample(self.memory, batch_size)

    def length(self):
        return len(self.memory)

#学習に使用するモデル
Model = nn.Sequential(
                    nn.Linear(in_features=27,out_features=54),
                    nn.ReLU(),
                    nn.Linear(in_features=54,out_features=108),
                    nn.ReLU(),
                    nn.Linear(in_features=108,out_features=216),
                    nn.ReLU(),
                    nn.Linear(in_features=216,out_features=5),
                    nn.Softmax(dim=0)
                    )
#更新対象となるネットワーク 
Model1P = Model
Model2P = Model
#更新を計算するためのモデル
Model1P_Target = Model
Model2P_Target = Model
#ここからが実際の学習のコード
# TODO:Replay Memoryの実装
# TODO:誤差逆伝播

optimizer = optim.Adam(Model.parameters(),lr=0.001,weight_decay=0.005)

MaxSteps = 500
episodes = 10000
CurrentStep = 0
TotalStep = 0
gamma = 0.99
epsiron = 1.0
eps_end = 0.01
eps_reduce_rate = 0.001
memory_size = 10000
batch_size = 32
#ReplayMemory
Memory_1P = ReplayMemory(memory_size)
Memory_2P = ReplayMemory(memory_size)
#トレーニングするよう設定。推論時はFalseにする。
Model1P.train(True)
Model2P.train(True)
Model1P_Target.train(True)
Model2P_Target.train(True)
criterion = nn.SmoothL1Loss()
env = UnityEnvironment(file_name="CardBattle", base_port=5005,side_channels=[])
env.reset()
#エージェントグループのリストを取得(グループ数は時間とともに変化する可能性があるが、今回は変化しないと分かっているのでループの外に出す)
agent_groups = env.get_agent_groups()
for episode in range(episodes+1):
    CurrentStep = 0
    #必要なデータを取得(本当は関数化したいが上手くいかないので直書き)
    #エージェントの状態を取得
    agent_group_specs = [env.get_agent_group_spec(agentgroup) for agentgroup in agent_groups]
    #各エージェントごとのBatchedStepResultを取得
    batched_step_results = [env.get_step_result(agentgroup) for agentgroup in agent_groups]
    agent_ids = [batched_step_result.agent_id for batched_step_result in batched_step_results] 
    #各エージェントごとのStepResultを取得
    step_results = [batched_step_results[int(agent_id)].get_agent_step_result(int(agent_id)) for agent_id in agent_ids]
    #observation値を取得
    observatiuons_from_batched_step_results = [batched_step_result.obs for batched_step_result in batched_step_results]
    observatiuons_from_step_results = [step_result.obs for step_result in step_results]
    #報酬を取得
    rewards_from_batched_step_results = [batched_step_result.reward for batched_step_result in batched_step_results]
    rewards_from_step_results = [step_result.reward for step_result in step_results]
    Input1P = observatiuons_from_step_results[0]
    Input2P = observatiuons_from_step_results[1]
    ret_action1P = Model1P(torch.from_numpy(np.array(Input1P)))
    ret_action2P = Model2P(torch.from_numpy(np.array(Input2P)))
    #ここからターゲットネットワークの訓練
    #TODO:入力をReplayMemoryに
    #順伝播
    out1P = Model1P_Target(torch.from_numpy(np.array(observatiuons_from_step_results[0])))
    out2P = Model2P_Target(torch.from_numpy(np.array(observatiuons_from_step_results[1])))
    #TODO:ターゲットをどうするか
    loss1P = criterion(out1P,out1P)
    loss2P = criterion(out2P,out2P)
    optimizer.zero_grad()
    loss1P.backward()
    loss2P.backward()
    optimizer.step()
    for i in range(MaxSteps):
        CurrentStep += 1
        TotalStep += 1
        if epsiron > eps_end :
            epsiron -= eps_reduce_rate

        #エージェントの状態を取得
        agent_group_specs = [env.get_agent_group_spec(agentgroup) for agentgroup in agent_groups]
        #各エージェントごとのBatchedStepResultを取得
        batched_step_results = [env.get_step_result(agentgroup) for agentgroup in agent_groups]
        agent_ids = [batched_step_result.agent_id for batched_step_result in batched_step_results] 
        #各エージェントごとのStepResultを取得
        step_results = [batched_step_results[int(agent_id)].get_agent_step_result(int(agent_id)) for agent_id in agent_ids]
        #observation値を取得 (状態となる)
        #observatiuons_from_batched_step_results = [batched_step_result.obs for batched_step_result in batched_step_results]
        observatiuons_from_step_results = [step_result.obs for step_result in step_results]
        #報酬を取得
        #rewards_from_batched_step_results = [batched_step_result.reward for batched_step_result in batched_step_results]
        rewards_from_step_results = [step_result.reward for step_result in step_results]
        Reward1P = rewards_from_step_results[0]
        Reward2P = rewards_from_step_results[1]
        State1P = observatiuons_from_step_results[0]
        State2P = observatiuons_from_step_results[1]
        ret_action1P = Model1P(torch.from_numpy(np.array(State1P)))
        ret_action2P = Model2P(torch.from_numpy(np.array(State2P)))

        if epsiron > np.random.rand():
            action1P = np.random.randn(5)
            action2P = np.random.randn(5)
        else:
            action1P = ret_action1P.detach().clone().numpy()
            action2P = ret_action2P.detach().clone().numpy()
            action1P = action1P[0]
            action2P = action2P[0]
        #エージェントごとに行動を指定
        env.set_action_for_agent(agent_groups[0],agent_ids[0],action1P)
        env.set_action_for_agent(agent_groups[1],agent_ids[1],action2P)
        #環境を１ステップ進める
        env.step()
        #各エージェントごとのBatchedStepResultを取得
        batched_step_results = [env.get_step_result(agentgroup) for agentgroup in agent_groups]
        agent_ids = [batched_step_result.agent_id for batched_step_result in batched_step_results] 
        #各エージェントごとのStepResultを取得
        step_results = [batched_step_results[int(agent_id)].get_agent_step_result(int(agent_id)) for agent_id in agent_ids]
        #observation値を取得 (状態となる)
        observatiuons_from_step_results = [step_result.obs for step_result in step_results]
        #「次の状態」を格納
        NextState1P = observatiuons_from_step_results[0]
        NextState2P = observatiuons_from_step_results[1]
        if CurrentStep > batch_size:
            #ReplayMemoryに格納(1Pから)
            Experience1P = []
            Experience2P = []
            Experience1P.extend(State1P)
            Experience1P.extend(action1P)
            Experience1P.extend(Reward1P)
            Experience1P.extend(NextState1P)
            #2Pも同様に格納
            Experience2P.extend(State2P)
            Experience2P.extend(action2P)
            Experience2P.extend(Reward2P)
            Experience2P.extend(NextState2P)
            Memory_1P.load(Experience1P)
            Memory_2P.load(Experience2P)

        #エピソード完了時
        if batched_step_results[0].done == True or batched_step_results[1].done == True:
            NextState1P = np.zeros(observatiuons_from_step_results[0].shape)
            NextState2P = np.zeros(observatiuons_from_step_results[1].shape)
            if CurrentStep > batch_size:
                #ReplayMemoryに格納(1Pから)
                Experience1P = []
                Experience2P = []
                Experience1P.extend(State1P)
                Experience1P.extend(action1P)
                Experience1P.extend(Reward1P)
                Experience1P.extend(NextState1P)
                #2Pも同様に格納
                Experience2P.extend(State2P)
                Experience2P.extend(action2P)
                Experience2P.extend(Reward2P)
                Experience2P.extend(NextState2P)
                Memory_1P.load(Experience1P)
                Memory_2P.load(Experience2P)
               

#環境のシャットダウン(プログラム終了)
env.close()