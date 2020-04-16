﻿using System.Collections;
using System.Collections.Generic;
using UnityEngine;

// プレイヤーのクラス

public class Player
{
    public short HP; //HP
    public LinkedList<Card> hands; //手札にあるカード
    public bool is1P; //1Pか？(2Pならfalse)
    public bool defendedflag; //ガードされているか？(デフォルトはfalse)
    public short ATK; //攻撃力
    public short DEF; //防御力

    //ここから先は定数類
    public const short StartHP = 1000; //HPの初期値
    public const short StartATK = 200; //攻撃力の初期値
    public const short StartDEF = 50;  //防御力の初期値

    

    //コンストラクタで初期化する
    public Player(bool isPlayer1){
        HP = StartHP;
        hands = new LinkedList<Card>();
        is1P = isPlayer1;
        defendedflag = false;
        ATK = StartATK;
        DEF = StartDEF;

    }
}
