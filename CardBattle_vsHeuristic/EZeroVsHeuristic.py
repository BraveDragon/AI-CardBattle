#coding: "utf-8"
from mlagents_envs.environment import UnityEnvironment
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision.transforms as T
import numpy as np
from collections import deque
import random
import EZeroModel
#ELOレーティング用のライブラリ(MITライセンスなので多分大丈夫だがライセンスは要確認)
from elote import EloCompetitor

#必要なクラス等を定義
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

#更新対象となるネットワーク
Devise = torch.device("cuda" if torch.cuda.is_available() else "cpu")
Model1P = EZeroModel.Model.to(Devise)
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
Model1P_Target = EZeroModel.Model.to(Devise)
#Model2P_Target = EZeroModel.Model.to(Devise)
#ここからが実際の学習のコード
optimizer = optim.Adam(EZeroModel.Model.parameters(),lr=0.001,weight_decay=0.005)
MaxSteps = 500
episodes = 10000
CurrentStep = 0
TotalStep = 0
gamma = 0.99

eps_reduce_rate = 0.001
memory_size = 10000
batch_size = 32
JustLooking = 10
#ReplayMemory
Memory_1P = ReplayMemory(memory_size)
#トレーニングするよう設定。推論時はFalseにする。
Model1P.train(True)
Model1P_Target.train(True)
criterion = nn.SmoothL1Loss()
env = UnityEnvironment(file_name="CardBattle", base_port=5005,side_channels=[])
env.reset()
#エージェントグループのリストを取得(グループ数は時間とともに変化する可能性があるが、今回は変化しないと分かっているのでループの外に出す)
agent_groups = env.get_agent_groups()

for episode in range(episodes+1):
    CurrentStep = 0
    #ここからターゲットネットワークの訓練
    if TotalStep == 0:
        #一番最初は楽観的初期化する
        target1P = torch.ones(EZeroModel.Outputs)
        out1P = Model1P_Target(torch.ones(EZeroModel.Inputs))
        loss1P = criterion(out1P,target1P)
        optimizer.zero_grad()
        loss1P.backward(retain_graph=True)
        optimizer.step()
    else:
        Model1P_Target.load_state_dict(Model1P.state_dict())
        pass

    for i in range(MaxSteps):
        CurrentStep += 1
        TotalStep += 1
        #エージェントの状態を取得
        agent_group_specs = [env.get_agent_group_spec(agentgroup) for agentgroup in agent_groups]
        #各エージェントごとのBatchedStepResultを取得
        batched_step_results = [env.get_step_result(agentgroup) for agentgroup in agent_groups]
        agent_ids = [batched_step_result.agent_id for batched_step_result in batched_step_results] 
        #各エージェントごとのStepResultを取得
        step_results = [batched_step_results[int(agent_id)].get_agent_step_result(int(agent_id)) for agent_id in agent_ids]
        #observation値を取得 (状態に相当)
        observations_from_step_results = [step_result.obs for step_result in step_results]
        #報酬を取得
        rewards_from_step_results = [step_result.reward for step_result in step_results]
        Reward1P = rewards_from_step_results[0]
        State1P = observations_from_step_results[0]
        State1P_tmp = State1P[0]
        if State1P_tmp[2] <= 0 or State1P_tmp[6] <= 0:
            TotalGameCount += 1
        #2Pの勝利
        if State1P_tmp[2] <= 0:
             Agent2P.beat(Agent1P)
             GameCount += 1
             Winning_2P += 1
        #1Pの勝利
        if State1P_tmp[6] <= 0:
             Agent1P.beat(Agent2P)
             GameCount += 1
             Winning_1P += 1
        #レーティングを書き出し
        with open("Model_EZero/Model1PRating.csv", "a") as f:
            f.write(str(TotalGameCount)+","+str(Agent1P.rating)+"\n")
        with open("Model_EZero/Model2PRating.csv", "a") as f:
            f.write(str(TotalGameCount)+","+str(Agent2P.rating)+"\n")
        #レーティングを表示(表示したらGameCount,Winning_1P,Winning_2Pをリセット)
        if GameCount > GameCount_ResultView:
             print("Rating : " + str(Agent1P.rating)+" "+str(Winning_1P / GameCount_ResultView)+ " | " + str(Agent2P.rating) +" "+str(Winning_2P / GameCount_ResultView))
             GameCount = 0
             Winning_1P = 0
             Winning_2P = 0

        action1P = np.random.randn(5)
        Load_Inputs1P = []
        if Memory_1P.length() > batch_size:
            Raw_Inputs1P = Memory_1P.sample(batch_size)
            Inputs1P = []
            for Ret_Input1P in range(len(Ret_Inputs1P)):
                Inputs1P.extend(Ret_Inputs1P[Ret_Input1P])
            Inputs1P = np.array(Inputs1P)
            
            for Input_itr in Inputs1P:
                if hasattr(Input_itr, "__iter__"):
                    Load_Inputs1P.extend(Input_itr)
                else:
                    Load_Inputs1P.append(Input_itr)
            Load_Inputs1P = np.array(Load_Inputs1P,dtype=np.float32)
            ret_action1P = Model1P(torch.from_numpy(Load_Inputs1P))
            action1P = ret_action1P.detach().clone().numpy()

        #エージェントごとに行動を指定
        env.set_action_for_agent(agent_groups[0],agent_ids[0],np.array(action1P))
        #環境を１ステップ進める
        try:
            env.step()
        except:
            #ゲームが外部から切られたら保存して終了する
            torch.save(Model1P.state_dict(),"Model_EZero/Model1P")
            #モデルをOnnx型式でも保存する(Unityなどから呼び出せるようにするため)
            torch.onnx.export(Model1P,torch.from_numpy(Load_Inputs1P),"Model_EZero/Model1P.onnx")
            exit()

        #各エージェントごとのBatchedStepResultを取得
        batched_step_results = [env.get_step_result(agentgroup) for agentgroup in agent_groups]
        agent_ids = [batched_step_result.agent_id for batched_step_result in batched_step_results] 
        #各エージェントごとのStepResultを取得
        step_results = [batched_step_results[int(agent_id)].get_agent_step_result(int(agent_id)) for agent_id in agent_ids]
        #observation値を取得 (状態に相当)
        observations_from_step_results = [step_result.obs for step_result in step_results]
        #「次の状態」を格納
        NextState1P = observations_from_step_results[0]
        if CurrentStep > JustLooking:
            #ReplayMemoryに格納(1Pから)
            Experience1P = []
            Reward1P = [float(Reward1P)]
            Experience1P.extend(State1P)
            Experience1P.extend(action1P)
            Experience1P.extend(Reward1P)
            Experience1P.extend(NextState1P)
            Memory_1P.load(Experience1P)
            pass
        State1P = NextState1P
        if Memory_1P.length() > batch_size:
            Ret_Inputs1P = Memory_1P.sample(batch_size)
            Inputs1P = []
            for Ret_Input in range(len(Ret_Inputs1P)):
                Inputs1P.extend(Ret_Inputs1P[Ret_Input])
            Inputs1P = np.array(Inputs1P)
            Load_Inputs1P = []
            for Input_itr in Inputs1P:
                if hasattr(Input_itr, "__iter__"):
                    Load_Inputs1P.extend(Input_itr)
                else:
                    Load_Inputs1P.append(Input_itr)
            Load_Inputs1P = np.array(Load_Inputs1P,dtype=np.float32)
            Output_Train = Model1P(torch.from_numpy(Load_Inputs1P))
            Output_Target = Model1P_Target(torch.from_numpy(Load_Inputs1P))
            criterion(Output_Train,Output_Target)
            optimizer.zero_grad()
            loss1P.backward(retain_graph=True)
            optimizer.step()
        #エピソード完了時
        if batched_step_results[0].done == True:
            NextState1P = np.zeros(observations_from_step_results[0].shape)
            if CurrentStep > JustLooking:
                #ReplayMemoryに格納
                Experience1P = []
                Experience1P.extend(State1P)
                Experience1P.extend(action1P.tolist())
                Experience1P.extend(Reward1P)
                Experience1P.extend(NextState1P)
                Memory_1P.load(Experience1P)
                
               
#モデルを保存
torch.save(Model1P.state_dict(),"Model_EZero/Model1P")
#モデルをOnnx型式でも保存する(Unityなどから呼び出せるようにするため)
torch.onnx.export(Model1P,torch.from_numpy(Load_Inputs1P),"Model_EZero/Model1P.onnx")
#環境のシャットダウン(プログラム終了)
env.close()