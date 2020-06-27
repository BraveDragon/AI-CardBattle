using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class CardText : MonoBehaviour {
    public Text text; //カード名
    public bool is1P;//1Pか？(2Pならfalse)
    public Card card_showing; //表示するカード
    [SerializeField] private Image cardfront;
    [NonSerialized] public bool isfront; //カードが表向きか？

    private void Start()
    {
        text.text = card_showing.CardName;
        isfront = is1P;
        text.enabled = isfront;
        cardfront.enabled = isfront;
    }
    private void Update(){
        text.enabled = isfront;
        cardfront.enabled = isfront;
    }

    public void OnClicked()
    {
        if (is1P == true)
        {
            GameManager.SetAction(this, true);


        }
    }

}
