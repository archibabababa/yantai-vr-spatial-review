using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using Valve.VR;

public class RightControl : MonoBehaviour
{

    public GameObject box1, box2, box3;

    bool isRoto;
    int numberScale,numberY;

    public SteamVR_Action_Boolean GrabPinch = SteamVR_Input.GetAction<SteamVR_Action_Boolean>("GrabPinch");
    
    public SteamVR_Action_Boolean GrabGrip = SteamVR_Input.GetAction<SteamVR_Action_Boolean>("GrabGrip");

    public SteamVR_Action_Boolean menu = SteamVR_Input.GetAction<SteamVR_Action_Boolean>("menu");
    void Start()
    {
        
    }

    void RototionControl()
    {
        if (isRoto)
        {
            box1.transform.Rotate(Vector3.up * 5 * Time.deltaTime);
            box2.transform.Rotate(Vector3.up * 5 * Time.deltaTime);
            box3.transform.Rotate(Vector3.up * 5 * Time.deltaTime);
        }
        
    }

    void Update()
    {
        RototionControl();

        if (menu.GetStateDown(SteamVR_Input_Sources.RightHand))
        {
            numberY++;
            if (numberY <= 4)
            {
                box1.transform.localScale += new Vector3(0, 0.002f, 0);
                box2.transform.localScale += new Vector3(0, 0.002f, 0);
                box3.transform.localScale += new Vector3(0, 0.002f, 0);
            }
            else if (numberY >= 5 && numberY <= 8)
            {
                box1.transform.localScale -= new Vector3(0, 0.002f, 0);
                box2.transform.localScale -= new Vector3(0, 0.002f, 0);
                box3.transform.localScale -= new Vector3(0, 0.002f, 0);
            }
            else
            {
                numberY = 0;
            }
        }

        if (GrabGrip.GetState(SteamVR_Input_Sources.RightHand))//右手持握键模型向外移动
        {
            box1.transform.Translate(Vector3.left * Time.deltaTime * 0.5f);
            box2.transform.Translate(Vector3.forward * Time.deltaTime * 0.5f);
            box3.transform.Translate(Vector3.forward * Time.deltaTime * 0.5f);
        }

        if (GrabGrip.GetState(SteamVR_Input_Sources.LeftHand))//左手持握键向里移动
        {
            box1.transform.Translate(-Vector3.left * Time.deltaTime * 0.5f);
            box2.transform.Translate(-Vector3.forward * Time.deltaTime * 0.5f);
            box3.transform.Translate(-Vector3.forward * Time.deltaTime * 0.5f);
        }

        if (GrabPinch.GetStateDown(SteamVR_Input_Sources.RightHand))
        {
            isRoto = true;
        }
        else if (GrabPinch.GetStateUp(SteamVR_Input_Sources.RightHand))
        {
            isRoto = false;
        }

        if (GrabPinch.GetStateDown(SteamVR_Input_Sources.LeftHand))
        {
            numberScale++;
            if (numberScale <= 4)
            {
                box1.transform.localScale -= new Vector3(0.002f, 0.002f, 0.002f);
                box2.transform.localScale -= new Vector3(0.002f, 0.002f, 0.002f);
                box3.transform.localScale -= new Vector3(0.002f, 0.002f, 0.002f);
            }
            else if(numberScale >= 5&&numberScale<=8)
            {
                box1.transform.localScale += new Vector3(0.002f, 0.002f, 0.002f);
                box2.transform.localScale += new Vector3(0.002f, 0.002f, 0.002f);
                box3.transform.localScale += new Vector3(0.002f, 0.002f, 0.002f);
            }
            else
            {
                numberScale = 0;
            }
        }
       
    }

    
}