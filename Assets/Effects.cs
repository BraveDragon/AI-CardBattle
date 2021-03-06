﻿using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;
using System.Linq;

//効果をまとめて記述

public class Effects : MonoBehaviour
{
    
   
    //以下、カードの効果を書いていく
    // void型で引数に bool is1P を取るpublic関数で定義
    //攻撃
    public void Attack(bool is1P) {


        if (is1P == true && GameManager.SelectedCard_2P.CardName != "Guard") {
            GameManager.player2.HP -= (short)(GameManager.player1.ATK - GameManager.player2.DEF);
           
        }
        if (is1P == false && GameManager.SelectedCard.CardName != "Guard") {
            GameManager.player1.HP -= (short)(GameManager.player2.ATK - GameManager.player1.DEF);
           
        }

    }

    //手札1枚をランダムに破棄する代わりに相手に2倍ダメージ
    public void Assult(bool is1P){
        if(is1P == true){
            List<CardText> cards = new List<CardText>(GameManager.Field_1P_tmp.GetComponentsInChildren<CardText>());
            CardText[] mine = cards.Where(x => x == GameManager.SelectedCard_Object.GetComponent<CardText>()).ToArray();
            cards.Remove(mine[0]);
            Destroy(cards[UnityEngine.Random.Range(0, cards.Count)].gameObject);
            if (GameManager.SelectedCard_2P.CardName != "Guard") {
                GameManager.player2.HP -= (short)(2 * GameManager.player1.ATK - GameManager.player2.DEF);
            }
        }
        if(is1P == false){
            List<CardText> cards = new List<CardText>(GameManager.Field_1P_tmp.GetComponentsInChildren<CardText>());
            CardText[] mine = cards.Where(x => x == GameManager.SelectedCard_Object.GetComponent<CardText>()).ToArray();
            cards.Remove(mine[0]);
            Destroy(cards[UnityEngine.Random.Range(0, cards.Count)].gameObject);
            if (GameManager.SelectedCard.CardName != "Guard") {
                GameManager.player1.HP -= (short)(2 * GameManager.player2.ATK - GameManager.player1.DEF);
            }
        }

    }

    //防御
    public void Guard(bool is1P) {
        if (is1P == true) {
            GameManager.player1.defendedflag = true;
            

        }
        if(is1P == false) {
            GameManager.player2.defendedflag = true;
            
        }
    }

    //回復
    public void Heal(bool is1P) {
        if (is1P == true)
        {
            
            GameManager.player1.HP += (short)(Player.StartHP * 0.3);
            if (GameManager.player1.HP > Player.StartHP) { GameManager.player1.HP = Player.StartHP; }
        }
        if(is1P == false)
        {
           
            GameManager.player2.HP += (short)(Player.StartHP * 0.3);
            if (GameManager.player2.HP > Player.StartHP) { GameManager.player2.HP = Player.StartHP; }
        }
    }

    public void ATKAdd200(bool is1P){
        if (is1P == true){ GameManager.player1.ATK += 200; }
        if (is1P == false) { GameManager.player2.ATK += 200; }
    }

    public void DEFAdd20(bool is1P){
        if (is1P == true) { GameManager.player1.DEF += 20; }
        if (is1P == false) { GameManager.player2.DEF += 20; }
    }

    public void ATKMinus100(bool is1P){
       if (is1P == true && GameManager.player2.ATK > 100){ GameManager.player2.ATK -= 100; }
       if (is1P == false && GameManager.player1.ATK > 100) { GameManager.player1.ATK -= 100; }
    }

    public void DEFMinus10(bool is1P)
    {
        if (is1P == true && GameManager.player2.DEF >= 10) { GameManager.player2.DEF -= 10; }
        if (is1P == false && GameManager.player1.DEF >= 10) { GameManager.player1.DEF -= 10; }
    }

    public void Counter(bool is1P){
        if (is1P == true && GameManager.SelectedCard_2P.CardName != "Guard")
        {
            
            GameManager.player2.HP -= (short)(GameManager.player2.ATK - GameManager.player2.DEF);

        }
        if(is1P == false && GameManager.SelectedCard.CardName != "Guard")
        {
            GameManager.player1.HP -= (short)(GameManager.player1.ATK - GameManager.player1.DEF);

        }
    }

    public void Gamble(bool is1P){
        float rand = UnityEngine.Random.Range(0.0f, 1.0f);
        if (is1P == true && rand >= 0.5f){
            GameManager.player2.HP = (short)(GameManager.player2.HP / 2);

        }
        if(is1P == false && rand >= 0.5f) {
            GameManager.player1.HP = (short)(GameManager.player1.HP / 2);
        }
    }

    public void Draw2(bool is1P){
        if (is1P == true)
        {
            byte handcount = (byte)GameManager.Field_1P_tmp.GetComponentsInChildren<CardText>().Length;
            for (byte i = 0; i < 2; i++) {
                //手札が上限いっぱいならカードを引かずに抜ける
                if(handcount >= Player.MaxHand){
                    //break;


                }
                Card drawcard = CardResources.OneDraw();
                GameObject card = Instantiate(GameManager.ViewCards_tmp, GameManager.Field_1P_tmp.transform, false);
                card.GetComponent<CardText>().card_showing = drawcard;
                card.GetComponent<CardText>().is1P = true;
            }

        }

        if(is1P == false)
        {
            byte handcount = (byte)GameManager.Field_2P_tmp.GetComponentsInChildren<CardText>().Length;
            for (byte i = 0; i < 2; i++) {
                //手札が上限いっぱいならカードを引かずに抜ける
                if (handcount >= Player.MaxHand){
                    break;
                }
                Card drawcard = CardResources.OneDraw();
                GameObject card = Instantiate(GameManager.ViewCards_tmp, GameManager.Field_2P_tmp.transform, false);
                card.GetComponent<CardText>().card_showing = drawcard;
                card.GetComponent<CardText>().is1P = false;


            }
        }

        
    }

    //カードを全部捨てて4枚引き直す
    public void NewDeal(bool is1P){
        if (is1P == true)
        {
            GameManager.IsNewDealt_1P = true;
            List<CardText> cards = new List<CardText>(GameManager.Field_1P_tmp.GetComponentsInChildren<CardText>());
            CardText[] mine = cards.Where(x => x == GameManager.SelectedCard_Object.GetComponent<CardText>()).ToArray();
            cards.Remove(mine[0]);
            foreach(CardText cardText in cards){
                Destroy(cardText.gameObject);
            }
            for (byte i = 0; i < Player.StartHand ; i++)
            {
                Card draw1P = CardResources.OneDraw();
                GameObject card1P;
                card1P = Instantiate(GameManager.ViewCards_tmp, GameManager.Field_1P_tmp.transform, false);
                card1P.GetComponent<CardText>().card_showing = draw1P;
                card1P.GetComponent<CardText>().is1P = true;
            }
            

        }
       if (is1P == false)
        {
            GameManager.IsNewDealt_2P = true;
            List<CardText> cards = new List<CardText>(GameManager.Field_2P_tmp.GetComponentsInChildren<CardText>());
            CardText[] mine = cards.Where(x => x == GameManager.SelectedCard_2P_Object.GetComponent<CardText>()).ToArray();
            cards.Remove(mine[0]);
            foreach (CardText cardText in cards)
            {
                Destroy(cardText.gameObject);
            }
            for (byte i = 0; i < Player.StartHand; i++)
            {
                Card draw2P = CardResources.OneDraw();
                GameObject card2P = Instantiate(GameManager.ViewCards_tmp, GameManager.Field_2P_tmp.transform, false);
                card2P.GetComponent<CardText>().card_showing = draw2P;
                card2P.GetComponent<CardText>().is1P = false;


            }

        }

       

    }

    //50%の確率で体力全回復
    public void Fortune(bool is1P) {
        float rand = UnityEngine.Random.Range(0.0f, 1.0f);
        if(is1P == true && rand >= 0.5f) {
            GameManager.player1.HP = Player.StartHP;
        }
        if(is1P == false && rand >= 0.5f) {
            GameManager.player2.HP = Player.StartHP;
        }
    }

    //ランダムに1枚使用するカード。RandomをGameManagerのInspectorビューの一番下に置くこと
    public void Random(bool is1P){
        
        int card = 0;
        card = UnityEngine.Random.Range(0,CardResources.AllCards.Count-1);
        CardResources.AllCards[card].Effect.Invoke(is1P);
    }


}
