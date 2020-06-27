#coding: "utf-8"
#chainerの学習済みモデルで推論を行う
from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.registry import UnityEnvRegistry
import chainer
import chainer.functions as F
import chainer.links as L
from chainer.serializers import save_npz
from chainer import serializers
import chainerrl
import numpy as np
import cupy as cp
import Memory
import pickle
import ChainerDQN

memory_size = 10000
Input_size = 1664
batch_size = 32

#ReplayMemoryの読み込み
Memory1P = Memory.ReplayMemory(memory_size)
Memory2P = Memory.ReplayMemory(memory_size)

with open("Memory1P.pkl", "rb") as f:
    Memory1P = pickle.load(f)

with open("Memory2P.pkl", "rb") as f:
    Memory2P = pickle.load(f)

#モデルの読み込み
Model1P = ChainerDQN.DQN(Input_size, ChainerDQN.Outputs)
Model2P = ChainerDQN.DQN(Input_size, ChainerDQN.Outputs)

serializers.load_npz("Model1P.npz",Model1P)
serializers.load_npz("Model2P.npz",Model2P)
Model1P.to_gpu(0)
Model2P.to_gpu(0)

registry = UnityEnvRegistry()
registry.register_from_yaml("CardBattle.yaml")

env = registry["CardBattle"].make()
env.reset()
agent_groups = list(env.behavior_specs.keys())

while True:
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
    try:
        env.step()
    except:
        exit()
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

    #ReplayMemoryに格納(1Pから)
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

    #2Pも同様に格納
    Experience2P.extend(State2P.tolist()[0])
    Experience2P.extend(action2P.tolist())
    Experience2P.extend(Reward2P.tolist())
    Experience2P.extend(NextState2P)
    Memory1P.load(Experience1P)
    Memory2P.load(Experience2P)
        
    State1P = NextState1P
    State2P = NextState2P




