using System.Collections.Generic;
using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.Sensors;
using Unity.MLAgents.Sensors.Reflection;
using System.Linq;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Policies;

public class PlayAgent : Agent
{
    [SerializeField] private GameObject Field;
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
    
    readonly string[] names = System.Enum.GetNames(typeof(GameManager.Steps));

    private void Awake() {
        is1P_tmp = is1P;
        
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
            if (is1P == true && GameManager.Field_1P_tmp.GetComponentsInChildren<CardText>().Length > 0)
            {
                CardText[] hands = GameManager.Field_1P_tmp.GetComponentsInChildren<CardText>().ToArray<CardText>();
                foreach (CardText card in hands)
                {
                    inputs.Add(card.card_showing.id);
                }
            }



            if (is1P == false && GameManager.Field_2P_tmp.GetComponentsInChildren<CardText>().Length > 0)
            {
                CardText[] hands = GameManager.Field_2P_tmp.GetComponentsInChildren<CardText>().ToArray<CardText>();
                foreach (CardText card in hands)
                {
                    inputs.Add(card.card_showing.id);
                }
            }

            

        }
        catch (System.NullReferenceException)
        {
            //ヌルリの原因・解決方法が分からないのでとりあえず握りつぶす
        }

    }

    public override void Initialize()
    {
        
        
    }

    public override void OnEpisodeBegin()
    {
        GameManager.step = GameManager.Steps.Standby;
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
        try {
            if (is1P == true && 
                GameManager.Field_1P_tmp != null &&
                GameManager.Field_1P_tmp.GetComponentsInChildren<CardText>().Length > 0) {
                CardText[] hands = GameManager.Field_1P_tmp.GetComponentsInChildren<CardText>().ToArray<CardText>();
                for(byte i= 0; i < Player.MaxHand; i++){
                    if(i < hands.Count()) {
                        sensor.AddObservation(hands[i].card_showing.id);
                    }
                    else {
                        sensor.AddObservation(0);
                    }
                }
                    
                    
            }



            if (is1P == false && 
                GameManager.Field_2P_tmp != null &&
                GameManager.Field_2P_tmp.GetComponentsInChildren<CardText>().Length > 0) {
                CardText[] hands = GameManager.Field_2P_tmp.GetComponentsInChildren<CardText>().ToArray<CardText>();
                for(byte i= 0; i < Player.MaxHand; i++){
                    if(i < hands.Count()) {
                         sensor.AddObservation(hands[i].card_showing.id);
                    }
                    else {
                        sensor.AddObservation(0);
                    }
                 
                }
               
            }

        }
        catch (System.NullReferenceException) {  
            //ヌルリの原因・解決方法が分からないのでとりあえず握りつぶす
        }

        

    }

    public override void OnActionReceived(ActionBuffers vectorAction) {

        if(GameManager.step == GameManager.Steps.KeyWait) {
            //vectorActionの最大値を求める関係で要素数が2以上の時のみ処理
            if (vectorAction.ContinuousActions.Length >= 2)
            {


                byte select = 0;
                float max = vectorAction.ContinuousActions.Max();
                for (byte i = 0; i < vectorAction.ContinuousActions.Length; i++)
                {
                    if (vectorAction.ContinuousActions[i] == max)
                    {
                        select = i;
                        break;
                    }
                }

                CardText[] hands = Field.GetComponentsInChildren<CardText>();



                if (is1P == true) { 
                    //手札に触れる関係上添え字が要素数を超えないようにする
                    if (select < hands.Count()) {
                        GameManager.SetAction(hands[select],is1P);
                    }
                    else {
                        GameManager.SetAction(hands[Random.Range(0,hands.Count())],is1P);
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
                    if (select < hands.Count()) {
                        GameManager.SetAction(hands[select], is1P);
                    }
                    else {
                        GameManager.SetAction(hands[Random.Range(0,hands.Count())],is1P);
                    }

                    //勝利時の処理
                    if (GameManager.player1.HP <= 0) {
                        SetReward(1.0f);
                        EndEpisode();

                    }
                    //敗北時の処理
                    if (GameManager.player2.HP <= 0) {
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
    
    public override void Heuristic(in ActionBuffers actionsOut)
    {
        if (GameManager.step == GameManager.Steps.KeyWait) {
            //共通して使用する変数類を定義+初期化
            //自分の手札を取得
            List<CardText> Hands = new List<CardText>(Field.GetComponentsInChildren<CardText>());
            CardText selectedcard = GetComponent<CardText>();
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
                //手札になかった時はランダムに選ぶ
                if (cardTexts.Count == 0){
                    byte index = (byte)Random.Range(0, Hands.Count);
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
                        break; //見つかればここでループを抜ける
                    }  
                }
                //最善のカードが手札になかった時
                if (cardTexts.Count == 0) {
                    for (byte i = 0; i < PickCards_Behind.Length; i++) {
                        cardTexts.AddRange(Hands.Where(hand => hand.card_showing.CardName == PickCards_Lead[i]));
                        if (cardTexts.Count > 0) {
                            selectedcard = cardTexts[0];
                            break; //見つかればここでループを抜ける
                        }
                    }
                }
                //手札になかった時はランダムに選ぶ
                if (cardTexts.Count == 0) {
                    byte index = (byte)Random.Range(0, Hands.Count);
                    selectedcard = Hands[index];
                }

            }

            GameManager.SetAction(selectedcard,is1P);
            m = 0;
            Hands.Clear();
        }

        // actionsOut = new float[0];
        }
      
    }

