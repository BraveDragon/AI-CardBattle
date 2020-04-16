using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class CardText : MonoBehaviour
{
    public Text text;
    public bool is1P;//1Pか？(2Pならfalse)
    public Card card_showing; //表示するカード

    private void Start()
    {
        text.text = card_showing.CardName;
    }

    public void OnClicked()
    {
        if (is1P == true)
        {
            ReturnCard(true);
            

        }
    }

    //カードを出力
    public void ReturnCard(bool is1P){
        if (is1P == true) {
            GameManager.SelectedCard = card_showing;
            GameManager.SelectedCard_Object = this.gameObject;
        }

        if(is1P == false) {
            GameManager.SelectedCard_2P = card_showing;
            GameManager.SelectedCard_2P_Object = this.gameObject;

        }


    }
}
