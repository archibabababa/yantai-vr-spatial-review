using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Rototion : MonoBehaviour
{
    public static Rototion GetRototion;

    public bool isRoto;
    void Start()
    {
        GetRototion = this;
    }

    // Update is called once per frame
    void Update()
    {
        if (isRoto)
        {
            transform.Rotate(Vector3.up * 5 * Time.deltaTime);
        }
    }
}
