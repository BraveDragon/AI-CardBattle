using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;

[CreateAssetMenu(fileName ="Card",menuName ="Create Card")]
//カードを表現するためのクラス(ScriptabeleObjectを使用)
public class Card : ScriptableObject
{
    public string CardName; //名前
    public byte id; //カードの通し番号
    public Sprite Cardgraph; //カードの絵
    //TODO:表面の画像を用意
    //public string EffectDescription; //効果の説明文
    [SerializeField] public EffectEvent Effect = new EffectEvent(); //効果
    
    
}

[System.Serializable] public class EffectEvent : UnityEvent<bool> {}
