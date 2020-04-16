using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class HPManager : MonoBehaviour
{
    public Slider HP_1P;
    public Slider HP_2P;
    public Text ATK_1P;
    public Text ATK_2P;
    public Text DEF_1P;
    public Text DEF_2P;
    public Text First_1P;
    public Text First_2P;

    // Start is called before the first frame update
    void Start()
    {
        HP_1P.maxValue = Player.StartHP;
        HP_2P.maxValue = Player.StartHP;
    }

    // Update is called once per frame
    void Update()
    {
        if (GameManager.player1 != null && GameManager.player2 != null) {
            HP_1P.value = GameManager.player1.HP;
            HP_2P.value = GameManager.player2.HP;
            ATK_1P.text = "ATK：" + string.Format("{0:00000}", GameManager.player1.ATK.ToString());
            ATK_2P.text = "ATK：" + string.Format("{0:00000}", GameManager.player2.ATK.ToString());
            DEF_1P.text = "DEF：" + string.Format("{0:00000}", GameManager.player1.DEF.ToString());
            DEF_2P.text = "DEF：" + string.Format("{0:00000}", GameManager.player2.DEF.ToString());
        }
        if(GameManager.Is1PFirst == true){
            First_1P.enabled = true;
            First_2P.enabled = false;
        }
        else{
            First_1P.enabled = false;
            First_2P.enabled = true;
        }

    }
}
