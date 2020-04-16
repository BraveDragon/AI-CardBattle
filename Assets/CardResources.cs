using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;

public class CardResources : MonoBehaviour
{
    public static List<Card> AllCards = new List<Card>();
    private Object[] objects;
    
    //デバッグ用。確認後消すこと
    public List<Card> Allcards_tmp = new List<Card>();

    private void Awake()
    {
        
        objects = Resources.LoadAll("Cards/",typeof(Card));
        foreach(Card card in objects){
            AllCards.Add(card);
        }
        Allcards_tmp = AllCards;

       
    }

  
    public static List<Card> Draw(byte draws)
    {
        int index = 0;
        List<Card> drawcards = new List<Card>();
        for (byte i = 0; i < draws; i++)
        {
            index = Random.Range(0,AllCards.Count);
            drawcards.Add(AllCards[index]);
        }

        return drawcards;



    }

    public static Card OneDraw()
    {
        int index = 0;
        Card drawcard = ScriptableObject.CreateInstance<Card>();
       
            index = Random.Range(0, AllCards.Count);
            drawcard = AllCards[index];
        

        return drawcard;



    }


    
}

