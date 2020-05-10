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
    List<int> inputs = new List<int>();
    public bool is1P;
    public static bool is1P_tmp;
    private byte m = 0; //モード
    //以下：各モードの説明
    // 0:自分と相手の体力を比較。
    // 1:優勢時。自分の体力が相手より多い。
    // 2:劣勢時。自分の体力が相手より少ない。
    //HPで有利な時に優先して使用するカード。添え字が小さいほど優先度高。
    private readonly string[] PickCards_Lead = {"ATK+200", "DEF-10", "NewDeal", "Random", "Gamble" };
    //HPで不利な時に優先して使用するカード。添え字が小さいほど優先度高。
    private readonly string[] PickCards_Behind = {"ATK-100", "DEF+20", "NewDeal", "Random" };
    //private short Player_HP_prev; //前のターンのプレイヤーのHP
    //private short Enemy_HP_prev; //前のターンの敵のHP
    //private short current_player_hp; //現在のプレイヤーのHP
    //private short current_enemy_hp; //現在の敵のHP

    readonly string[] names = System.Enum.GetNames(typeof(GameManager.Steps));
    //SideChannel sideChannel;

    private void Awake()
    {
        is1P_tmp = is1P;
        if (OnnxModel != null) {
            model = ModelLoader.Load(OnnxModel);
            worker = WorkerFactory.CreateWorker(WorkerFactory.Type.ComputePrecompiled, model);
        }
        //sideChannel = new CardGameSideChannel();
        //Academy.Instance.RegisterSideChannel(sideChannel);
        
    }

    private void Update()
    {
        //TODO: ReplayMemoryの実装
        
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
        if (OnnxModel != null) {
            Tensor tensor = new Tensor(inputs.ToArray());
            worker.Execute(tensor);
        }
        

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
                        GameManager.SetAction(hands[select],is1P);
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
                        GameManager.SetAction(hands[select], is1P);
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
    
    //優勢時に最優先で使うべきカードを返す
    private string[] GetBestCard_Lead(){
        if(GameManager.player1.ATK >= GameManager.player2.ATK) {
            string[] ret = { "Attack", "Counter" };
            return ret;
        }
        else {
            string[] ret = { "Counter", "Attack" };
            return ret;
        }
    }

    //劣勢時に最優先で使うべきカードを返す
    private string[] GetBestCard_Behind() {
        if(GameManager.Is1PFirst == true) {
            string[] ret = {"Heal", "Guard" };
            return ret;
        } else {
            string[] ret = {"Heal"};
            return ret;
        }
    }
    
    public override float[] Heuristic()
    {
        if (GameManager.step == GameManager.Steps.KeyWait) {
            //共通して使用する変数類を定義+初期化
            //自分の手札を取得
            List<CardText> Hands = new List<CardText>(Field.GetComponentsInChildren<CardText>());
            CardText selectedcard = new CardText();
            
            //学習済みモデルがある時
            if (OnnxModel != null) {
                Tensor o = worker.PeekOutput();
                inputs.Clear();
                byte index;
                List<float> outputlist = new List<float>();
                for (byte i = 0; i < o.channels; i++) {
                    outputlist.Add(o[0, 0, 0, i]);
                    //Debug.Log(outputlist.Count);
                }
                o.Dispose();

                
                //TODO:行動を返り値に反映させる
                index = (byte)Mathf.RoundToInt(outputlist.Average());

                outputlist.Clear();
                if (Hands.Count < index) {
                    index = 0;
                }
                //Debug.Log(index);
              
                //GameManager.SetAction(Hands[index].card_showing, Hands[index].gameObject,is1P);
                    
                
                //if (is1P == false) {
                //    GameManager.SelectedCard_2P = AgentsHands[index].card_showing;
                //    GameManager.SelectedCard_2P_Object = AgentsHands[index].gameObject;
                //}
                

                return outputlist.ToArray();


            }
            //ルールベースの戦略を使用して戦うAI
            //自分のHPと相手のHPを確認
            if (m == 0) {
                if (is1P == true) {
                    if (GameManager.player1.HP >= GameManager.player2.HP) {
                        m = 1;
                    } else {
                        m = 2;
                    }
                }
                if (is1P == false) {
                    if (GameManager.player2.HP >= GameManager.player1.HP) {
                        m = 1;
                    } else {
                        m = 2;
                    }
                }

            }
            //優勢時の処理
            if(m == 1) {
                string[] bestcards = GetBestCard_Lead();
                List<CardText> cardTexts = new List<CardText>();
                for (byte i = 0; i < bestcards.Length; i++){
                    cardTexts.AddRange(Hands.Where(hand => hand.card_showing.CardName == bestcards[i]));
                     if(cardTexts.Count > 0){
                        selectedcard = cardTexts[0];
                        break;
                    }
                    }
                //最善のカードが手札になかった時
                if(cardTexts.Count == 0){
                    for (byte i = 0; i < PickCards_Lead.Length; i++){
                        cardTexts.AddRange(Hands.Where(hand => hand.card_showing.CardName == PickCards_Lead[i]));
                        if (cardTexts.Count > 0) {
                            selectedcard = cardTexts[0];
                            break; //カードが見つかればここでループを抜ける
                        }
                    }
                }
                //2回カードを探しても手札になかった時は手札にあるカードからランダムに選ぶ
                if (cardTexts.Count == 0){
                    //byte actionindex = 0;
                    byte index = (byte)Random.Range(0, Hands.Count);
                    //float[] action = new float[Hands.Count];
                    //for (byte i = 0; i < Hands.Count; i++){
                    //    action[i] = 0.0f;
                    //}
                    //action[actionindex] = 1.0f;
                    //GameManager.SetAction(Hands[index].card_showing, Hands[index].gameObject, is1P);
                    //m = 0;
                    //return action.ToArray();
                    selectedcard = Hands[index];
                }

                }
            if (m == 2) {
                string[] bestcards = GetBestCard_Behind();
                List<CardText> cardTexts = new List<CardText>();
                for (byte i = 0; i < bestcards.Length; i++) {
                    cardTexts.AddRange(Hands.Where(hand => hand.card_showing.CardName == bestcards[i]));
                    if (cardTexts.Count > 0) {
                        selectedcard = cardTexts[0];
                        break; //カードが見つかればここでループを抜ける
                    }  
                }
                //最善のカードが手札になかった時
                if (cardTexts.Count == 0) {
                    for (byte i = 0; i < PickCards_Behind.Length; i++) {
                        cardTexts.AddRange(Hands.Where(hand => hand.card_showing.CardName == PickCards_Lead[i]));
                        if (cardTexts.Count > 0) {
                            selectedcard = cardTexts[0];
                            break; //カードが見つかればここでループを抜ける
                        }
                    }
                }
                //2回カードを探しても手札になかった時は手札にあるカードからランダムに選ぶ
                if (cardTexts.Count == 0) {
                    //byte actionindex = 0;
                    //float[] action = new float[AgentsHands.Count];
                    byte index = (byte)Random.Range(0, Hands.Count);
                    selectedcard = Hands[index];
                    //for (byte i = 0; i < AgentsHands.Count; i++)
                    //{
                    //    action[i] = 0.0f;
                    //}
                    //action[actionindex] = 1.0f;
                    
                    //return action.ToArray();
                }

            }

            GameManager.SetAction(selectedcard,is1P);
            //Debug.Log(index);
            m = 0;
            Hands.Clear();
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

        //

        //AgentsHands.Clear();
        return new float[0];
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
