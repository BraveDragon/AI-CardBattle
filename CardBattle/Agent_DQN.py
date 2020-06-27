#coding: "utf-8"
from mlagents_envs.environment import UnityEnvironment
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
from collections import deque
import DQNModel
#ELOレーティング用のライブラリ(MITライセンスなので多分大丈夫だがライセンスは要確認)
from elote import EloCompetitor
import Memory
import pprint

#問題の箇所を確認するための設定
torch.autograd.set_detect_anomaly(True)



#更新対象となるネットワーク
Devise = "cuda" if torch.cuda.is_available() else "cpu"
Model1P = DQNModel.Model.to(Devise)
Model2P = DQNModel.Model.to(Devise)
#レーティング評価を行うためのクラス
Agent1P = EloCompetitor()
Agent2P = EloCompetitor()
#ゲーム回数のカウント((GameCount_ResultView) 回ごとに結果を出力)
GameCount = 0
#累計ゲーム回数のカウント
TotalGameCount = 0
#何回目のゲームごとに結果を出力するか
GameCount_ResultView = 100
#1P,2Pそれぞれの勝利回数
Winning_1P = 0
Winning_2P = 0
#更新を計算するためのモデル
Model1P_Target = DQNModel.Model.to(Devise)
Model2P_Target = DQNModel.Model.to(Devise)
#ここからが実際の学習のコード
optimizer1P = optim.Adam(DQNModel.Model.parameters(),lr=0.001,weight_decay=0.005)
optimizer2P = optim.Adam(DQNModel.Model.parameters(),lr=0.001,weight_decay=0.005)

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
JustLooking = 10
#楽観的初期化の回数
StartInitializeTimes = 10

Need_Retain_Init = True
Need_Retain_1P = True
Need_Retain_2P = True
#ReplayMemory
Memory_1P = Memory.ReplayMemory(memory_size)
Memory_2P = Memory.ReplayMemory(memory_size)
#トレーニングするよう設定。推論時はFalseにする。
Model1P.train(True)
Model2P.train(True)
Model1P_Target.train(True)
Model2P_Target.train(True)
criterion = nn.SmoothL1Loss()
env = UnityEnvironment(file_name="CardBattle", base_port=5005,side_channels=[])
env.reset()
#エージェントグループのリストを取得(グループ数は時間とともに変化する可能性があるが、今回は変化しないと分かっているのでループの外に出す)
agent_groups = env.get_behavior_names()

target1P = torch.ones(DQNModel.Outputs,dtype=torch.float32,device=Devise)
target2P = torch.ones(DQNModel.Outputs,dtype=torch.float32,device=Devise)
firstinput = torch.ones(DQNModel.Inputs,dtype=torch.float32,device=Devise).clone()
out1P = Model1P_Target(firstinput).clone()
out2P = Model2P_Target(firstinput).clone()
loss1P = criterion(out1P,target1P)
loss2P = criterion(out2P,target2P)
optimizer1P.zero_grad()
optimizer2P.zero_grad()
loss1P.backward(retain_graph=Need_Retain_Init)
loss2P.backward(retain_graph=Need_Retain_Init)
Need_Retain_First = False
optimizer1P.step()
optimizer2P.step()

#一番最初は楽観的初期化する
# for i in range(StartInitializeTimes-1):
#     #TODO: 直下の行で発生したエラーの修正
#     target1P = torch.ones(DQNModel.Outputs,dtype=torch.float32,device=Devise)
#     target2P = torch.ones(DQNModel.Outputs,dtype=torch.float32,device=Devise)
#     out1P = Model1P_Target(torch.tensor([1 for i in range(DQNModel.Inputs)],dtype=torch.float32,device=Devise).clone())
#     out2P = Model2P_Target(torch.tensor([1 for i in range(DQNModel.Inputs)],dtype=torch.float32,device=Devise).clone())
#     loss1P = criterion(out1P,target1P)
#     loss2P = criterion(out2P,target2P)
#     optimizer1P.zero_grad()
#     optimizer2P.zero_grad()
#     loss1P.backward(retain_graph=Need_Retain_Init)
#     loss2P.backward(retain_graph=Need_Retain_Init)
#     Need_Retain_First = False
#     optimizer1P.step()
#     optimizer2P.step()

for episode in range(episodes+1):
    CurrentStep = 0
    Model1P_Target.load_state_dict(Model1P.state_dict())
    Model2P_Target.load_state_dict(Model2P.state_dict())
    
    for i in range(MaxSteps):
        CurrentStep += 1
        TotalStep += 1
        if epsiron > eps_end :
            epsiron -= eps_reduce_rate

        #エージェントの状態を取得
        agent_group_specs = [env.get_behavior_spec(agentgroup) for agentgroup in agent_groups]
        #各エージェントごとのBatchedStepResultを取得
        batched_step_results = [env.get_steps(agentgroup) for agentgroup in agent_groups]
        agent_ids = [batched_step_results[0][0].agent_id, batched_step_results[1][0].agent_id] 
        #各エージェントごとのStepResultを取得
        step_results = [batched_step_results[0][0], batched_step_results[1][0]] 
        #observation値を取得 (状態に相当)
        observations_from_step_results = [step_result.obs for step_result in step_results]
        #報酬を取得
        rewards_from_step_results = [step_result.reward for step_result in step_results]
        Reward1P = rewards_from_step_results[0]
        Reward2P = rewards_from_step_results[1]
        State1P = observations_from_step_results[0]
        State2P = observations_from_step_results[1]
        State1P_tmp = State1P[0]
        State2P_tmp = State2P[0]
        if step_results[0].obs[0][0][2] <= 0 or step_results[1].obs[0][0][2] <= 0 or \
           step_results[0].obs[0][0][6] <= 0 or step_results[1].obs[0][0][6] <= 0:
            TotalGameCount += 1
        #2Pの勝利
        if step_results[0].obs[0][0][2] <= 0 or step_results[1].obs[0][0][2] <= 0:
             Agent2P.beat(Agent1P)
             GameCount += 1
             Winning_2P += 1
        #1Pの勝利
        if step_results[0].obs[0][0][6] <= 0 or step_results[1].obs[0][0][6] <= 0:
             Agent1P.beat(Agent2P)
             GameCount += 1
             Winning_1P += 1

        if epsiron > np.random.rand():
            action1P = np.random.randn(5)
            action2P = np.random.randn(5)
        elif Memory_1P.length() > batch_size and Memory_2P.length() > batch_size:
            Inputs1P = np.array(Memory_1P.sample(batch_size))
            #Inputs1P = Inputs1P.reshape((32,8))
            Load_Inputs1P = []
            for Input_itr in Inputs1P[:,:]:
                Load_Inputs1P.extend(Input_itr)

            Load_Inputs1P = torch.tensor(Load_Inputs1P,dtype=torch.float32,device=Devise)
            ret_action1P = Model1P(Load_Inputs1P.clone())

            Inputs2P = np.array(Memory_2P.sample(batch_size))
            #Inputs2P = Inputs2P.reshape((32,8))
            Load_Inputs2P = []
            for Input_itr in Inputs2P[:,:]:
                if hasattr(Input_itr, "__iter__"):
                    Load_Inputs2P.extend(Input_itr)
                else:
                    Load_Inputs2P.append(Input_itr)
            Load_Inputs2P = torch.tensor(Load_Inputs2P,dtype=torch.float32,device=Devise)
            ret_action2P = Model2P(Load_Inputs2P.clone())

            ret_action1P = ret_action1P.to('cpu')
            ret_action2P = ret_action2P.to('cpu')
            action1P = ret_action1P.detach().clone().numpy()
            action2P = ret_action2P.detach().clone().numpy()
            
        #エージェントごとに行動を指定
        env.set_action_for_agent(agent_groups[0],agent_ids[0],np.array(action1P))
        env.set_action_for_agent(agent_groups[1],agent_ids[1],np.array(action2P))
        #環境を１ステップ進める
        try:
            env.step()
        except:
            #ゲームが外部から切られたら保存して終了する
            torch.save(Model1P.state_dict(),"Model/Model1P.pth")
            torch.save(Model2P.state_dict(),"Model/Model2P.pth")
            exit()

        #各エージェントごとのBatchedStepResultを取得
        batched_step_results = [env.get_steps(agentgroup) for agentgroup in agent_groups]
        agent_ids = [batched_step_results[0][0].agent_id, batched_step_results[1][0].agent_id] 
        #各エージェントごとのStepResultを取得
        step_results = [batched_step_results[0][0], batched_step_results[1][0]]
        #observation値を取得 (状態に相当)
        observations_from_step_results = [step_result.obs for step_result in step_results]
        #「次の状態」を格納
        NextState1P = observations_from_step_results[0]
        NextState2P = observations_from_step_results[1]
        if CurrentStep > JustLooking:
            #ReplayMemoryに格納(1Pから)
            Experience1P = []
            Experience2P = []
            
            State =  State1P[0].tolist()
            NextState = NextState1P[0].tolist()

            Experience1P.extend(State[0])
            Experience1P.extend(action1P)
            Experience1P.extend(Reward1P)
            Experience1P.extend(NextState[0])

            #2Pも同様に格納
            State = State2P[0].tolist()
            NextState = NextState2P[0].tolist()

            Experience2P.extend(State[0])
            Experience2P.extend(action2P)
            Experience2P.extend(Reward2P)
            Experience2P.extend(NextState2P[0])
            Memory_1P.load(Experience1P)
            Memory_2P.load(Experience2P)

        State1P = NextState1P
        State2P = NextState2P
        if Memory_1P.length() > batch_size:
            Inputs1P = torch.tensor(Memory_1P.sample(batch_size),dtype=torch.float32,device=Devise)
            #Inputs1P = Inputs1P.reshape((32,8))
            Load_Inputs1P = []
            for Input_itr in Inputs1P:
                    Load_Inputs1P.extend(Input_itr)
            Load_Inputs1P = torch.tensor(Load_Inputs1P,dtype=torch.float32,device=Devise).detach().clone()
            Output_Train = Model1P(Load_Inputs1P)
            Output_Target = Model1P_Target(Load_Inputs1P)
            criterion(Output_Train,Output_Target)
            optimizer1P.zero_grad()
            loss1P.backward(retain_graph=Need_Retain_1P)
            Need_Retain_1P = False
            optimizer1P.step()
        if Memory_2P.length() > batch_size:
            Inputs2P = torch.tensor(Memory_2P.sample(batch_size),dtype=torch.float32,device=Devise)
            #Inputs2P = Inputs2P.reshape((32,8))
            Load_Inputs2P = []
            for Input_itr in Inputs2P:
                if hasattr(Input_itr, "__iter__"):
                    Load_Inputs2P.extend(Input_itr)
                else:
                    Load_Inputs2P.append(Input_itr)

            Load_Inputs2P = torch.tensor(Load_Inputs2P,dtype=torch.float32,device=Devise).detach().clone()
            Output_Train = Model2P(Load_Inputs2P)
            Output_Target = Model2P_Target(Load_Inputs2P)
            criterion(Output_Train,Output_Target)
            optimizer2P.zero_grad()
            loss2P.backward(retain_graph=Need_Retain_2P)
            Need_Retain_2P = False
            optimizer2P.step()
        #エピソード完了時
        if len(batched_step_results[0][1].max_step) > 0 and len(batched_step_results[1][1].max_step) > 0:
            if batched_step_results[0][1].max_step[-1] == True or batched_step_results[1][1].max_step[-1] == True:
                NextState1P = np.zeros(observations_from_step_results[0].shape)
                NextState2P = np.zeros(observations_from_step_results[1].shape)
                if CurrentStep > JustLooking:
                    Experience1P = []
                    Experience2P = []
                    
                    State = State1P[0].tolist()
                    NextState = NextState1P[0].tolist()
                    Experience1P.extend(State[0])
                    Experience1P.extend(action1P)
                    Experience1P.extend(Reward1P)
                    Experience1P.extend(NextState[0])

                    State = State2P[0].tolist()
                    NextState = NextState2P[0].tolist()
                    Experience2P.extend(State[0])
                    Experience2P.extend(action2P)
                    Experience2P.extend(Reward2P)
                    Experience2P.extend(NextState[0])

                    #まとめてReplayMemoryに格納
                    Memory_1P.load(Experience1P)
                    Memory_2P.load(Experience2P)
               
#モデルを保存
torch.save(Model1P.state_dict(),"Model/Model1P.pth")
torch.save(Model2P.state_dict(),"Model/Model2P.pth")
#環境のシャットダウン(プログラム終了)
env.close()