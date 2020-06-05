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
#ReplayMemoryのデータをUnityと共有するために使用
#import json
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
Devise = "cuda" if torch.cuda.is_available() else "cpu"
Model1P = EZeroModel.Model.to(Devise)
Model2P = EZeroModel.Model.to(Devise)
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
Model2P_Target = EZeroModel.Model.to(Devise)
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
agent_groups = env.get_behavior_names()

for episode in range(episodes+1):
    CurrentStep = 0
    #ここからターゲットネットワークの訓練
    if TotalStep == 0:
        #一番最初は初期化する
        target1P = torch.from_numpy(np.random.rand(EZeroModel.Outputs)).to(Devise).float()
        target2P = torch.from_numpy(np.random.rand(EZeroModel.Outputs)).to(Devise).float()
        out1P = Model1P_Target(torch.from_numpy(np.random.rand(EZeroModel.Inputs)).to(Devise).float())
        out2P = Model2P_Target(torch.from_numpy(np.random.rand(EZeroModel.Inputs)).to(Devise).float())
        loss1P = criterion(out1P,target1P)
        loss2P = criterion(out2P,target2P)
        optimizer.zero_grad()
        loss1P.backward(retain_graph=True)
        loss2P.backward(retain_graph=True)
        optimizer.step()
    else:
        Model1P_Target.load_state_dict(Model1P.state_dict())
        Model2P_Target.load_state_dict(Model2P.state_dict())
        pass

    for i in range(MaxSteps):
        CurrentStep += 1
        TotalStep += 1
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
        if step_results[0].obs[0][0][2] <= 0 or step_results[1].obs[0][0][2] <= 0 or step_results[0].obs[0][0][6] <= 0 or step_results[1].obs[0][0][6] <= 0:
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
        action2P = np.random.randn(5)
        if Memory_1P.length() > batch_size and Memory_2P.length() > batch_size:
            Raw_Inputs1P = Memory_1P.sample(batch_size)
            Inputs1P = []
            for Ret_Input1P in range(len(Raw_Inputs1P)):
                Inputs1P.extend(Ret_Inputs1P[Ret_Input1P])
            Inputs1P = np.array(Inputs1P)
            Load_Inputs1P = []
            for Input_itr in Inputs1P:
                if hasattr(Input_itr, "__iter__"):
                    Load_Inputs1P.extend(Input_itr)
                else:
                    Load_Inputs1P.append(Input_itr)
            Load_Inputs1P = np.array(Load_Inputs1P,dtype=np.float32)
            ret_action1P = Model1P(torch.from_numpy(Load_Inputs1P))

            Raw_Input2P = Memory_2P.sample(batch_size)
            Inputs2P = []
            for Ret_Input2P in range(len(Raw_Input2P)):
                Inputs2P.extend(Raw_Input2P[Ret_Input2P])
            Inputs2P = np.array(Inputs2P)
            Load_Inputs2P = []
            for Input_itr in Inputs2P:
                if hasattr(Input_itr, "__iter__"):
                    Load_Inputs2P.extend(Input_itr)
                else:
                    Load_Inputs2P.append(Input_itr)
            Load_Inputs2P = np.array(Load_Inputs2P,dtype=np.float32)
            ret_action2P = Model2P(torch.from_numpy(Load_Inputs2P))

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
            torch.save(Model1P.state_dict(),"Model_EZero/Model1P.pth")
            torch.save(Model2P.state_dict(),"Model_EZero/Model2P.pth")
            #モデルをOnnx型式でも保存する(Unityなどから呼び出せるようにするため)
            # torch.onnx.export(Model1P,torch.from_numpy(Load_Inputs1P),"Model_EZero/Model1P.onnx")
            # torch.onnx.export(Model2P,torch.from_numpy(Load_Inputs2P),"Model_EZero/Model2P.onnx")
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
            Reward1P = [float(Reward1P)]
            Experience1P.extend(State1P)
            Experience1P.extend(action1P)
            Experience1P.extend(Reward1P)
            Experience1P.extend(NextState1P)
            #2Pも同様に格納
            Reward2P = [float(Reward2P)]
            Experience2P.extend(State2P)
            Experience2P.extend(action2P)
            Experience2P.extend(Reward2P)
            Experience2P.extend(NextState2P)
            # Experience1P_tmp = []
            # Experience2P_tmp = []
            # for Experience in Experience1P:
            #     if type(Experience) is np.ndarray:
            #         Experience1P_tmp.extend(Experience.tolist())
            #     else:
            #         Experience1P_tmp.append(float(Experience))
            # for Experience in Experience2P:
            #     if type(Experience) is np.ndarray:
            #         Experience2P_tmp.extend(Experience.tolist())
            #     else:
            #         Experience2P_tmp.append(float(Experience))
            
            # Memory1P = {"Memory": Experience1P_tmp}
            # Memory2P = {"Memory": Experience2P_tmp}
            # with open("Model_EZero/Model1PMemory.json", "a") as f:
            #     json.dump(Memory1P, f)

            # with open("Model_EZero/Model2PMemory.json", "a") as f:
            #     json.dump(Memory2P, f)
            Memory_1P.load(Experience1P)
            Memory_2P.load(Experience2P)
            pass
        State1P = NextState1P
        State2P = NextState2P
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
        if Memory_2P.length() > batch_size:
            Ret_Inputs = Memory_2P.sample(batch_size)
            Inputs2P = []
            for Ret_Input in range(len(Ret_Inputs)):
                Inputs2P.extend(Ret_Inputs[Ret_Input])
            Inputs2P = np.array(Inputs2P)
            Load_Inputs2P = []
            for Input_itr in Inputs2P:
                if hasattr(Input_itr, "__iter__"):
                    Load_Inputs2P.extend(Input_itr)
                else:
                    Load_Inputs2P.append(Input_itr)
            Load_Inputs2P = np.array(Load_Inputs2P,dtype=np.float32)
            Output_Train = Model2P(torch.from_numpy(Load_Inputs2P).to(Devise))
            Output_Target = Model2P_Target(torch.from_numpy(Load_Inputs2P).to(Devise))
            criterion(Output_Train,Output_Target)
            optimizer.zero_grad()
            loss2P.backward(retain_graph=True)
            optimizer.step()
        #エピソード完了時
        if len(batched_step_results[0][1].max_step) > 0 and len(batched_step_results[1][1].max_step) > 0:

            if batched_step_results[0][1].max_step[-1] == True or batched_step_results[1][1].max_step[-1] == True:
                NextState1P = np.zeros(observations_from_step_results[0].shape)
                NextState2P = np.zeros(observations_from_step_results[1].shape)
                if CurrentStep > JustLooking:
                    #ReplayMemoryに格納(1Pから)
                    Experience1P = []
                    Experience2P = []
                    Experience1P.extend(State1P)
                    Experience1P.extend(action1P.tolist())
                    Experience1P.extend(Reward1P)
                    Experience1P.extend(NextState1P)
                    #2Pも同様に格納
                    Experience2P.extend(State2P)
                    Experience2P.extend(action2P)
                    Experience2P.extend(Reward2P)
                    Experience2P.extend(NextState2P)
                    # Experience1P_tmp = []
                    # Experience2P_tmp = []
                    # for Experience in Experience1P:
                    #     if type(Experience) is np.ndarray:
                    #         Experience1P_tmp.extend(Experience.tolist())
                    #     else:
                    #         Experience1P_tmp.append(float(Experience))
                    # for Experience in Experience2P:
                    #     if type(Experience) is np.ndarray:
                    #         Experience2P_tmp.extend(Experience.tolist())
                    #     else:
                    #         Experience2P_tmp.append(float(Experience))
                    # Memory1P = {"Memory": Experience1P_tmp}
                    # Memory2P = {"Memory": Experience2P_tmp}
                    # with open("Model_EZero/Model1PMemory.json", "a") as f:
                    #     json.dump(Memory1P, f)
                
                    # with open("Model_EZero/Model2PMemory.json", "a") as f:
                    #     json.dump(Memory2P, f)
                    # Memory1P.clear()
                    # Memory2P.clear()
                    Memory_1P.load(Experience1P)
                    Memory_2P.load(Experience2P)
               
#モデルを保存
torch.save(Model1P.state_dict(),"Model_EZero/Model1P.pth")
torch.save(Model2P.state_dict(),"Model_EZero/Model2P.pth")
#モデルをOnnx型式でも保存する(Unityなどから呼び出せるようにするため)
# torch.onnx.export(Model1P,torch.from_numpy(Load_Inputs1P).to(Devise),"Model_EZero/Model1P.onnx")
# torch.onnx.export(Model2P,torch.from_numpy(Load_Inputs2P).to(Devise),"Model_EZero/Model2P.onnx")
#環境のシャットダウン(プログラム終了)
env.close()