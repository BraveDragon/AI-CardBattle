using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using MLAgents;
using MLAgents.Sensors;
using Barracuda;
using System.Linq;

public class PlayAgent : Agent
{
    [SerializeField] private GameObject Field;
    //Onnx形式のモデル
    public NNModel OnnxModel;
    private Model model;
    private IWorker worker;
    private Tensor Input_Tensor;
    List<CardText> AgentsHands = new List<CardText>();
    public bool is1P;
    public static bool is1P_tmp;
    //private short Player_HP_prev; //前のターンのプレイヤーのHP
    //private short Enemy_HP_prev; //前のターンの敵のHP
    //private short current_player_hp; //現在のプレイヤーのHP
    //private short current_enemy_hp; //現在の敵のHP

    readonly string[] names = System.Enum.GetNames(typeof(GameManager.Steps));
    //SideChannel sideChannel;

    private void Awake()
    {
        is1P_tmp = is1P;
        model = ModelLoader.Load(OnnxModel);
        worker = WorkerFactory.CreateWorker(WorkerFactory.Type.ComputePrecompiled, model);
        
        //sideChannel = new CardGameSideChannel();
        //Academy.Instance.RegisterSideChannel(sideChannel);
    }

    private void Update()
    {
        //TODO: ReplayMemoryの実装
        List<int> inputs = new List<int>();
        inputs.Add(GameManager.turn);
        inputs.AddRange(GameManager.GetOnehotStep());
        if (GameManager.player1 != null)
        {
            inputs.Add(GameManager.player1.ATK);
            inputs.Add(GameManager.player1.DEF);
            inputs.Add(GameManager.player1.HP);
            if (GameManager.player1.defendedflag == true)
            {
                inputs.Add(1);
            }
            if (GameManager.player1.defendedflag == false)
            {
                inputs.Add(0);
            }
        }
        if (GameManager.player2 != null){
            inputs.Add(GameManager.player2.ATK);
            inputs.Add(GameManager.player2.DEF);
            inputs.Add(GameManager.player2.HP);
            if (GameManager.player2.defendedflag == true)
            {
                inputs.Add(1);
            }
            if (GameManager.player2.defendedflag == false)
            {
                inputs.Add(0);
            }
        }
        try
        {
            if (is1P == true && GameManager.player1.hands != null)
            {
                Card[] hands = GameManager.player1.hands.ToArray();
                foreach (Card card in hands)
                {
                    inputs.Add(card.id);
                }
            }



            if (is1P == false && GameManager.player2.hands != null)
            {
                Card[] hands = GameManager.player2.hands.ToArray();
                foreach (Card card in hands)
                {
                    inputs.Add(card.id);
                }
            }

        }
        catch (System.NullReferenceException ex)
        {
            //ヌルリの原因・解決方法が分からないのでとりあえず握りつぶす
        }
        Input_Tensor = new Tensor(inputs.ToArray());
        worker.Execute(Input_Tensor);

    }

    public override void Initialize()
    {
        
        
    }

    public override void OnEpisodeBegin()
    {
        GameManager.step = GameManager.Steps.Standby;
        //Player_HP_prev = Player.StartHP;
        //Enemy_HP_prev = Player.StartHP;
    }

    
    public override void CollectObservations(VectorSensor sensor)
    {
        
        sensor.AddObservation(GameManager.turn);
        sensor.AddOneHotObservation((int)GameManager.step, names.Length);
        sensor.AddObservation(GameManager.Is1PFirst);

        if (GameManager.player1 != null)
        {
            sensor.AddObservation(GameManager.player1.ATK);
            sensor.AddObservation(GameManager.player1.DEF);
            sensor.AddObservation(GameManager.player1.HP);
            sensor.AddObservation(GameManager.player1.defendedflag);
            
            

        }

        if (GameManager.player2 != null)
        {
            sensor.AddObservation(GameManager.player2.ATK);
            sensor.AddObservation(GameManager.player2.DEF);
            sensor.AddObservation(GameManager.player2.HP);
            sensor.AddObservation(GameManager.player2.defendedflag);
            
            

        }
        try
        {
            if (is1P == true && GameManager.player1.hands != null)
            {
                Card[] hands = GameManager.player1.hands.ToArray();
                foreach (Card card in hands)
                {
                    sensor.AddObservation(card.id);
                    
                }
            }



            if (is1P == false && GameManager.player2.hands != null)
            {
                Card[] hands = GameManager.player2.hands.ToArray();
                foreach (Card card in hands)
                {
                    sensor.AddObservation(card.id);
                   
                }
            }

        }
        catch (System.NullReferenceException ex) {  
            //ヌルリの原因・解決方法が分からないのでとりあえず握りつぶす
        }

        

    }

    public override void OnActionReceived(float[] vectorAction) {
        
        //if (GameManager.step == GameManager.Steps.StartStep) {
        //    AddReward(-0.0001f); //ターンが長引くほどペナルティ
            
            //if (is1P == true) {
            //    current_player_hp = GameManager.player1.HP;
            //    current_enemy_hp = GameManager.player2.HP;
                
            //}
            //if(is1P == false) {
            //    current_player_hp = GameManager.player2.HP;
            //    current_enemy_hp = GameManager.player1.HP;
            //}
            //if(current_player_hp < Player_HP_prev){
            //    //AddReward(-0.3f);
            //}
            //if(current_player_hp >= Player_HP_prev){
            //    //AddReward(0.4f);
            //}
            //if(current_enemy_hp < Enemy_HP_prev){
            //    //AddReward(-0.2f);
            //}
            //if (current_enemy_hp > Enemy_HP_prev)
            //{
            //    //AddReward(0.3f);
            //}
        //}

        if(GameManager.step == GameManager.Steps.KeyWait) {
            //vectorActionの最大値を求める関係で要素数が2以上の時のみ処理
            if (vectorAction.Length >= 2)
            {


                byte select = 0;
                float max = vectorAction.Max();
                for (byte i = 0; i < vectorAction.Length; i++)
                {
                    if (vectorAction[i] == max)
                    {
                        select = i;
                        break;
                    }
                }

                CardText[] hands = Field.GetComponentsInChildren<CardText>();



                if (is1P == true) { //手札に触れる関係上添え字が要素数を超えないようにする

                    if (select < hands.Count()) {
                        GameManager.SelectedCard = hands[select].card_showing;
                        GameManager.SelectedCard_Object = hands[select].gameObject;
                    }
                    //勝利時の処理
                    if (GameManager.player2.HP <= 0)
                    {
                        SetReward(1.0f);
                        EndEpisode();

                    }
                    //敗北時の処理
                    if (GameManager.player1.HP <= 0)
                    {
                        SetReward(-1.0f);
                        EndEpisode();

                    }


                }
                if (is1P == false)
                {
                    //手札に触れる関係上添え字が要素数を超えないようにする
                    if (select < hands.Count())
                    {
                        GameManager.SelectedCard_2P = hands[select].card_showing;
                        GameManager.SelectedCard_2P_Object = hands[select].gameObject;
                    }

                    //勝利時の処理
                    if (GameManager.player1.HP <= 0)
                    {
                        SetReward(1.0f);
                        EndEpisode();

                    }
                    //敗北時の処理
                    if (GameManager.player2.HP <= 0)
                    {
                        SetReward(-1.0f);
                        EndEpisode();

                    }
                }
            }
        }
        



    }

    
    public override float[] Heuristic()
    {
        List<float> action = new List<float>();
        List<CardText> objects = new List<CardText>();
        if (GameManager.step == GameManager.Steps.KeyWait)
        {
            if(OnnxModel.Equals(null) == false) {
               
                Tensor output = worker.PeekOutput();
                float[] ret_action = output.AsFloats();
                float max = ret_action.Max();
                byte maxindex = 0;
                for(byte i = 0; i < ret_action.Length; i++){
                    if(ret_action[i] == max){
                        maxindex = i;
                        break;
                    }
                }

                objects.AddRange(Field.GetComponentsInChildren<CardText>());
                AgentsHands.AddRange(objects);
                if(AgentsHands.Count < maxindex) {
                    maxindex = 0;
                }
                if (is1P == true){
                    GameManager.SelectedCard = AgentsHands[maxindex].card_showing;
                    GameManager.SelectedCard_Object = AgentsHands[maxindex].gameObject;
                }
                if (is1P == false)
                {
                    GameManager.SelectedCard_2P = AgentsHands[maxindex].card_showing;
                    GameManager.SelectedCard_2P_Object = AgentsHands[maxindex].gameObject;
                }
                AgentsHands.Clear();
                return ret_action;

            }
            //仮組みでランダムに選ぶだけのAI
            //objects.AddRange(Field.GetComponentsInChildren<CardText>());
           
            //AgentsHands.AddRange(objects);
            //action.AddRange(Enumerable.Repeat(0.0f, AgentsHands.Count));

            //byte actionindex = 0;
            //actionindex = (byte)Random.Range(0, AgentsHands.Count);
            //for (byte i = 0; i < action.Count; i++)
            //    {
            //        action[i] = 0.0f;
            //    }
            //action[actionindex] = 1.0f;

            //AgentsHands[actionindex].ReturnCard(false);

            //AgentsHands.Clear();
            

        }
        return action.ToArray();
    }

    ~PlayAgent(){

        worker.Dispose();
    }


   
}

//サイドチャネル
//ここからデータを送る
//public class CardGameSideChannel : SideChannel
//{
//    public CardGameSideChannel(){
//        ChannelId = new System.Guid("00000000-0000-0000-0000-000000000000");
//    }

//    //Python側からのデータを受信
//    public override void OnMessageReceived(IncomingMessage msg)
//    {  
//        string message = msg.ReadString();
//        throw new System.NotImplementedException();
//    }

//    //データ送信処理
//    public void SendData() {
//        using (OutgoingMessage message = new OutgoingMessage()) {
//            //ゲーム全体の情報
//            message.WriteInt32(GameManager.turn);
//            //TODO：現在のステップをone-hot化して送る
//            //当面はただの数値として送る
//            message.WriteInt32((int)GameManager.step);
//            message.WriteBoolean(GameManager.Is1PFirst);

//            //ここから1Pの情報
//            message.WriteInt32(GameManager.player1.ATK);
//            message.WriteInt32(GameManager.player1.DEF);
//            message.WriteInt32(GameManager.player1.HP);
//            message.WriteBoolean(GameManager.player1.defendedflag);

//            //ここから2Pの情報
//            message.WriteInt32(GameManager.player2.ATK);
//            message.WriteInt32(GameManager.player2.DEF);
//            message.WriteInt32(GameManager.player2.HP);
//            message.WriteBoolean(GameManager.player2.defendedflag);

            
//            //TODO：手札(Agentがプレイしている方だけ)のデータを送る
//            if(PlayAgent.is1P_tmp == true){
//                Card[] hands = GameManager.player1.hands.ToArray();
//                string cards = JsonUtility.ToJson(hands);
//                       message.WriteString(cards);
//            }
//            if(PlayAgent.is1P_tmp == false){
//                Card[] hands = GameManager.player2.hands.ToArray();
//                string cards = JsonUtility.ToJson(hands);
//                message.WriteString(cards);
//            }
            
//            QueueMessageToSend(message);
//        }
//    }
   
//}
