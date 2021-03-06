﻿using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using System.Linq;
using Unity.MLAgents;
using System;

public class GameManager : MonoBehaviour {

    public static ushort turn; //ターン数
    public static Steps step; //ステップ
    public static Player player1; //1P
    public static Player player2; //2P
    public Text ResultText; //決着時のテキスト
    [SerializeField] private GameObject Field_1P; // 表示するカードの親オブジェクト(1P)
    [SerializeField] private GameObject Field_2P; // 表示するカードの親オブジェクト(2P)
    public static GameObject Field_1P_tmp;
    public static GameObject Field_2P_tmp;
    public GameObject ViewCards; //表示するカードのプレハブ
    public static GameObject ViewCards_tmp;
    
    
    public static bool Is1PFirst = true; //1Pが先攻か
    public static bool IsNewDealt_1P = false;
    public static bool IsNewDealt_2P = false;
    
    public static Card SelectedCard { get; private set; } //1Pが選択したカード(初期値はnull)
    public static GameObject SelectedCard_Object { get; private set; } //1Pが選択したカードのオブジェクト
    public static Card SelectedCard_2P { get; private set; } //2Pが選択したカード(初期値はnull)
    public static GameObject SelectedCard_2P_Object { get; private set; } //2Pが選択したカードのオブジェクト


    public enum Steps : byte{
        Standby, //準備
        KeyWait,//入力待ち
        StartStep, //ターン開始(第一ターンは飛ばす)
        Main,//効果の処理
        Action,//演出
        End,//ターン終了
        Result //結果表示
        
    }

    private void Awake()
    {
        Field_1P_tmp = Field_1P;
        Field_2P_tmp = Field_2P;
        ViewCards_tmp = ViewCards;
        SelectedCard = null;
        SelectedCard_2P = null;
        SelectedCard_Object = null;
        SelectedCard_2P_Object = null;
        
        turn = 0;
       
        
    }
    // Start is called before the first frame update
    void Start(){
        step = Steps.Standby;
    }

    //実際の処理を書く
    void Algorithm() {

        //if文でひたすら分岐
        if(step == Steps.Standby){
            StandBy();
        }
        if(step == Steps.KeyWait){
            KeyWait();
        }
        if(step == Steps.StartStep){
            StartStep();
        }
        if(step == Steps.Main){
            Main();
        }
        if(step == Steps.Action){
            Action();
        }
        if(step == Steps.End){
            End();
        }
        if(step == Steps.Result){
            Result();
        }
        
    }

    // Update is called once per frame
    void Update() {
        Algorithm();

    }

    private void StandBy() {
        //環境の初期化を行う
        if (UnityEngine.Random.Range(0, 2) == 0) { Is1PFirst = true; }
        else { Is1PFirst = false; }
        ResultText.text = "";
        player1 = new Player(true);
        player2 = new Player(false);
        //既にカードが存在しているなら消す
        player1.hands.Clear();
        player2.hands.Clear();
        CardText[] cardTexts1P = Field_1P_tmp.GetComponentsInChildren<CardText>();
        CardText[] cardTexts2P = Field_2P_tmp.GetComponentsInChildren<CardText>();
        foreach (CardText cardText in cardTexts1P)
            {
                Destroy(cardText.gameObject);
            }
        foreach (CardText cardText in cardTexts2P)
            {
                Destroy(cardText.gameObject);
            }

        //各種フラグを初期化する
        IsNewDealt_1P = false;
        IsNewDealt_2P = false;
        CardInitialize();

        step = Steps.KeyWait;
    }
    

    //最初のカードを配る
    public static void CardInitialize(){
        

        for (byte i = 0; i < Player.StartHand; i++)　{
            GameManager.player1.hands.AddFirst(CardResources.OneDraw());
            GameManager.player2.hands.AddFirst(CardResources.OneDraw());

        }
        GameObject ViewCard;
        List<CardText> cardtexts1P = new List<CardText>();
        List<CardText> cardtexts2P = new List<CardText>();
        Card[] player1_hand = player1.hands.ToArray();
        Card[] player2_hand = player2.hands.ToArray();
        



        for (byte i = 0; i < player1_hand.Length; i++)
        {
            cardtexts1P.AddRange(Field_1P_tmp.GetComponentsInChildren<CardText>());
            if (player1.hands.Count <= player1_hand.Length)
            {
                ViewCard = Instantiate(ViewCards_tmp, Field_1P_tmp.transform, false);
                ViewCard.GetComponent<CardText>().card_showing = player1_hand[i];
                ViewCard.GetComponent<CardText>().text.text = player1_hand[i].CardName;
                ViewCard.GetComponent<CardText>().is1P = true;
            }

        }

        for (byte i = 0; i < player2_hand.Length; i++)
        {
            cardtexts2P.AddRange(Field_2P_tmp.GetComponentsInChildren<CardText>());
            if (player2.hands.Count <= player2_hand.Length)
            {
                ViewCard = Instantiate(ViewCards_tmp, Field_2P_tmp.transform, false);
                ViewCard.GetComponent<CardText>().card_showing = player2_hand[i];
                ViewCard.GetComponent<CardText>().text.text = player2_hand[i].CardName;
                ViewCard.GetComponent<CardText>().text.enabled = false;
                ViewCard.GetComponent<CardText>().is1P = false;
            }

        }




    }

    void KeyWait() {
        if (SelectedCard != null &&
           SelectedCard_Object != null &&
           SelectedCard_2P != null &&
           SelectedCard_2P_Object != null) {

            step = Steps.Action;

        }

    }

    void StartStep()
    {
        //ターン初めのドロー(最初は飛ばす)
       
            Card draw1P = CardResources.OneDraw();
            GameObject card1P;
        if (Field_1P_tmp.GetComponentsInChildren<CardText>().Length < Player.MaxHand &&
            IsNewDealt_1P == false){
            card1P = Instantiate(ViewCards, Field_1P.transform, false);
            card1P.GetComponent<CardText>().card_showing = draw1P;
            card1P.GetComponent<CardText>().is1P = true;
            step = Steps.KeyWait;
        }
        if (Field_2P_tmp.GetComponentsInChildren<CardText>().Length < Player.MaxHand &&
            IsNewDealt_2P == false)
        {
            Card draw2P = CardResources.OneDraw();
            GameObject card2P;
            card2P = Instantiate(ViewCards, Field_2P.transform, false);
            card2P.GetComponent<CardText>().card_showing = draw2P;
            card2P.GetComponent<CardText>().is1P = false;
            step = Steps.KeyWait;
        }

        IsNewDealt_1P = false;
        IsNewDealt_2P = false;

    }

    void Action() {
        //演出を行う
        if (SelectedCard_2P_Object != null) {
            SelectedCard_2P_Object.GetComponent<CardText>().isfront = true;
        }
        //AIを学習させる時は一時停止しない
        if (SceneManager.GetActiveScene().name == "Main") {
            Invoke("showcard", 1.0f);
        } else {
             showcard();
        }
       
        step = Steps.Main;
    }


    void showcard() {
        Destroy(SelectedCard_Object);
        Destroy(SelectedCard_2P_Object);
        SelectedCard_Object = null;
        SelectedCard_2P_Object = null;
        SelectedCard = null;
        SelectedCard_2P = null;
        
    }

    void Main(){
        //1Pが先攻の時
        if(Is1PFirst == true){
            Main1P();//1Pの行動
            Main2P();//2Pの行動
        }

        //1Pが後攻の時
        if (Is1PFirst == false)
        {
            Main2P();//2Pの行動
            Main1P();//1Pの行動
        }
        
        step = Steps.End;

    }

    //1Pの処理
    void Main1P(){
        if (SelectedCard != null) {
            SelectedCard.Effect.Invoke(true); //効果を使用
           
            
        }


    }

    void Main2P(){
        if (SelectedCard_2P != null) {
            SelectedCard_2P.Effect.Invoke(false);
            
            

        }
        


    }

    

    
   

    //ターン終了時の処理
    void End(){
        
        
        //防御状態を解除
        player1.defendedflag = false;
            player2.defendedflag = false;
            

        if (player1.HP <= 0)
            {
                //1P敗北時の処理
                ResultText.text = "2P　WIN!";
                step = Steps.Result;

            }
            if (player2.HP <= 0)
            {
                //2P敗北時の処理
                ResultText.text = "1P　WIN!";
                step = Steps.Result;
            }

        //ゲームが続行できる時のみ処理
        if (player1.HP > 0 && player2.HP > 0) {
            //ターンを進める
            turn += 1;
            //ステップを最初に戻す
            if (SelectedCard_Object == null &&
                SelectedCard_2P_Object == null) {
                step = Steps.StartStep;
            }
        }
            
        
    }

    
    void Result() {

        if (SceneManager.GetActiveScene().name == "Main") {
            if (Input.GetKeyDown(KeyCode.Space) == true) {
                step = Steps.Standby;
            }
        } else {
            step = Steps.Standby;
        }
        
        

    }

    //選択したカードを受け取る
    public static void SetAction(CardText selectedcard, bool is1P) {
            if (is1P == true)
            {
                SelectedCard = selectedcard.card_showing;
                SelectedCard_Object = selectedcard.gameObject;
            }
            if (is1P == false)
            {
                SelectedCard_2P = selectedcard.card_showing;
                SelectedCard_2P_Object = selectedcard.gameObject;
            }
        
       
    }


    public static int[] GetOnehotStep()
    {
        int[] ret = new int[7];
        //一旦値を全て0で埋める
        for(byte i = 0; i < ret.Length; i++)
        {
            ret[i] = 1;
        }
        ret[(int)step] = 1;

        return ret;
    }
}

