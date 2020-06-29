#coding: "utf-8"
from mlagents_envs.environment import UnityEnvironment
import chainer
import chainer.functions as F
import chainer.links as L
from chainer.serializers import save_npz
import cupy as cp
import Memory
import ChainerDQN

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

#ゲーム回数のカウント((GameCount_ResultView) 回ごとに結果を出力)
GameCount = 0
#累計ゲーム回数のカウント
TotalGameCount = 0

Input_size = 1664

Memory1P = Memory.ReplayMemory(memory_size)
Memory2P = Memory.ReplayMemory(memory_size)

Model1P = ChainerDQN.DQN(Input_size,ChainerDQN.Outputs)
Model2P = ChainerDQN.DQN(Input_size,ChainerDQN.Outputs)
Model1P.to_gpu(0)
Model2P.to_gpu(0)

optimizer1P = chainer.optimizers.Adam(alpha=0.001,weight_decay_rate=0.005)
optimizer2P = chainer.optimizers.Adam(alpha=0.001,weight_decay_rate=0.005)
optimizer1P.setup(Model1P)
optimizer2P.setup(Model2P)

Model1P_Target = ChainerDQN.DQN(Input_size,ChainerDQN.Outputs)
Model2P_Target = ChainerDQN.DQN(Input_size,ChainerDQN.Outputs)
Model1P_Target.to_gpu(0)
Model2P_Target.to_gpu(0)

for i in range(StartInitializeTimes):
    target1P = cp.array([[1 for i in range(ChainerDQN.Outputs)]],dtype=cp.float32)
    target2P = cp.array([[1 for i in range(ChainerDQN.Outputs)]],dtype=cp.float32)
    out1P = Model1P_Target(cp.array([[1 for i in range(Input_size)]],dtype=cp.float32))
    out2P = Model2P_Target(cp.array([[1 for i in range(Input_size)]],dtype=cp.float32))
    loss1P = F.huber_loss(out1P,target1P,delta=1.0)
    loss2P = F.huber_loss(out2P,target2P,delta=1.0)
    Model1P_Target.cleargrads()
    Model2P_Target.cleargrads()
    loss1P.backward()
    loss2P.backward()
    
    optimizer1P.update()
    optimizer2P.update()






env = UnityEnvironment(file_name="CardBattle", base_port=5005,side_channels=[])
env.reset()
agent_groups = list(env.behavior_specs.keys())
#ここから学習ループ
for episode in range(episodes+1):
    CurrentStep = 0
    Model1P = Model1P_Target
    Model2P = Model2P_Target

    for i in range(MaxSteps):
        CurrentStep += 1
        TotalStep += 1
        if epsiron > eps_end :
            epsiron -= eps_reduce_rate

        #エージェントの状態を取得
        agent_group_specs = [env.behavior_specs[agentgroup] for agentgroup in agent_groups]
        #各エージェントごとのBatchedStepResultを取得
        batched_step_results = [env.get_steps(agentgroup) for agentgroup in agent_groups]
        agent_ids = [batched_step_results[0][0].agent_id, batched_step_results[1][0].agent_id] 
        #各エージェントごとのStepResultを取得
        step_results = [batched_step_results[0][0], batched_step_results[1][0]] 
        #observation値を取得 (状態に相当)
        observations_from_step_results = [step_result.obs for step_result in step_results]
        #報酬を取得
        rewards_from_step_results = [step_result.reward for step_result in step_results]
        Reward1P = cp.array(rewards_from_step_results[0],dtype=cp.float32)
        Reward2P = cp.array(rewards_from_step_results[1],dtype=cp.float32)
        State1P = cp.array(observations_from_step_results[0][0],dtype=cp.float32)
        State2P = cp.array(observations_from_step_results[1][0],dtype=cp.float32)
        
        if step_results[0].obs[0][0][2] <= 0 or step_results[1].obs[0][0][2] <= 0 or \
           step_results[0].obs[0][0][6] <= 0 or step_results[1].obs[0][0][6] <= 0:
            TotalGameCount += 1
        
        if epsiron > cp.random.rand() or \
           Memory1P.length() < batch_size and Memory2P.length() < batch_size:
            action1P = cp.random.randn(5)
            action2P = cp.random.randn(5)
            action1P = chainer.cuda.to_cpu(action1P)
            action2P = chainer.cuda.to_cpu(action2P)
        else:
            RawInput1P = Memory1P.sample(batch_size)
            RawInput2P = Memory2P.sample(batch_size)
            Input1P = []
            Input2P = []

            for i in RawInput1P:
                Input1P.extend(i)
            
            for i in RawInput2P:
                Input2P.extend(i)

            action1P = Model1P(cp.array([Input1P],dtype=cp.float32))
            action2P = Model2P(cp.array([Input2P],dtype=cp.float32))

            action1P = chainer.cuda.to_cpu(action1P.data[0])
            action2P = chainer.cuda.to_cpu(action2P.data[0])
        

        #エージェントごとに行動を指定
        env.set_action_for_agent(agent_groups[0],agent_ids[0],action1P)
        env.set_action_for_agent(agent_groups[1],agent_ids[1],action2P)
        #環境を１ステップ進める
        try:
            env.step()
        except:
            #ゲームが外部から切られたら保存して終了する
            Model1P.to_cpu()
            Model2P.to_cpu()
            save_npz('Model1P.npz',Model1P)
            save_npz('Model2P.npz',Model2P)
        
        #各エージェントごとのBatchedStepResultを取得
        batched_step_results = [env.get_steps(agentgroup) for agentgroup in agent_groups]
        agent_ids = [batched_step_results[0][0].agent_id, batched_step_results[1][0].agent_id] 
        #各エージェントごとのStepResultを取得
        step_results = [batched_step_results[0][0], batched_step_results[1][0]]
        #observation値を取得 (状態に相当)
        observations_from_step_results = [step_result.obs for step_result in step_results]
        #「次の状態」を格納
        NextState1P_tmp = observations_from_step_results[0]
        NextState2P_tmp = observations_from_step_results[1]
        NextState1P = []
        NextState2P = []
        if CurrentStep > JustLooking:
            #ReplayMemoryに格納(1Pから)
            Experience1P = []
            Experience2P = []
            try:
                for i in NextState1P_tmp:
                    if len(i) > 0:
                        NextState1P.extend(i.tolist()[0])
                for i in NextState2P_tmp:
                    if len(i) > 0:
                        NextState2P.extend(i.tolist()[0])
            except: 
                Model1P.to_cpu()
                Model2P.to_cpu()
                save_npz('Model1P.npz',Model1P)
                save_npz('Model2P.npz',Model2P)


            Experience1P.extend(State1P.tolist()[0])
            Experience1P.extend(action1P.tolist())
            Experience1P.extend(Reward1P.tolist())
            Experience1P.extend(NextState1P)

            #2Pも同様に格納
            Experience2P.extend(State2P.tolist()[0])
            Experience2P.extend(action2P.tolist())
            Experience2P.extend(Reward2P.tolist())
            Experience2P.extend(NextState2P)
            Memory1P.load(Experience1P)
            Memory2P.load(Experience2P)
        
        State1P = NextState1P
        State2P = NextState2P

        if Memory1P.length() > batch_size:
            RawInput1P = Memory1P.sample(batch_size)
            Input1P = []
            for i in RawInput1P:
                if hasattr(i,"__iter__"):
                    Input1P.extend(i)
                else:
                    Input1P.append(i)
            
            
            Output_Target1P = Model1P_Target(cp.array([Input1P],dtype=cp.float32))
            OutPut_Train1P = Model1P(cp.array([Input1P],dtype=cp.float32))
            loss1P = F.huber_loss(OutPut_Train1P,Output_Target1P,delta=1.0)
            Model1P.cleargrads()
            loss1P.backward()
            optimizer1P.update()
        
        if  Memory2P.length() > batch_size:
            RawInput2P = Memory2P.sample(batch_size)
            Input2P = []
            for i in RawInput2P:
                Input2P.extend(i)
            Output_Target2P = Model2P_Target(cp.array([Input2P],dtype=cp.float32))
            OutPut_Train2P = Model2P(cp.array([Input2P],dtype=cp.float32))
            loss2P = F.huber_loss(OutPut_Train2P,Output_Target2P,delta=1.0)
            Model2P.cleargrads()
            loss2P.backward()
            optimizer2P.update()
        
        #エピソード完了時
        if len(batched_step_results[0][1].interrupted) > 0 and len(batched_step_results[1][1].interrupted) > 0:
            if batched_step_results[0][1].interrupted[-1] == True or batched_step_results[1][1].interrupted[-1] == True:

                if CurrentStep > JustLooking:
                    Experience1P = []
                    Experience2P = []

                    for i in NextState1P_tmp:
                        NextState1P.extend(i.tolist()[0])
                    for i in NextState2P_tmp:
                        NextState2P.extend(i.tolist()[0])
                    
                    Experience1P.extend(State1P.tolist()[0])
                    Experience1P.extend(action1P.tolist())
                    Experience1P.extend(Reward1P.tolist())
                    Experience1P.extend(NextState1P)
                    
                    Experience2P.extend(State2P.tolist()[0])
                    Experience2P.extend(action2P.tolist())
                    Experience2P.extend(Reward2P.tolist())
                    Experience2P.extend(NextState2P)

                    #まとめてReplayMemoryに格納
                    Memory1P.load(Experience1P)
                    Memory2P.load(Experience2P)
                
                if Memory1P.length() > batch_size:
                    RawInput1P = Memory1P.sample(batch_size)
                    Input1P = []
                    for i in RawInput1P:
                        Input1P.extend(i)
                    Output_Target1P = Model1P_Target(cp.array([Input1P],dtype=cp.float32))
                    OutPut_Train1P = Model1P(cp.array([Input1P],dtype=cp.float32))
                    loss1P = F.huber_loss(OutPut_Train1P,Output_Target1P,delta=1.0)
                    Model1P.cleargrads()
                    loss1P.backward()
                    optimizer1P.update()

                if  Memory2P.length() > batch_size:
                    RawInput2P = Memory2P.sample(batch_size)
                    Input2P = []
                    for i in RawInput2P:
                        Input2P.extend(i)
                    
                    Output_Target2P = Model2P_Target(cp.array([Input2P],dtype=cp.float32))
                    OutPut_Train2P = Model2P(cp.array([Input2P],dtype=cp.float32))
                    loss2P = F.huber_loss(OutPut_Train2P,Output_Target2P,delta=1.0)
                    Model2P.cleargrads()
                    loss2P.backward()
                    optimizer2P.update()
                
#モデルを保存
Model1P.to_cpu()
Model2P.to_cpu()
save_npz('Model1P.npz',Model1P)
save_npz('Model2P.npz',Model2P)

#環境のシャットダウン(プログラム終了)
env.close()