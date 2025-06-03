using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class sphere : MonoBehaviour
{
    private Rigidbody Sphere;

    void Awake(){
        Sphere = gameObject.GetComponent<Rigidbody>();
    }

    // Start is called before the first frame update
    void Start()
    {
        StartCoroutine(Run());
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    IEnumerator Run(){
        while(Time.time < 2000.0f){
        Sphere.AddForce(Vector3.forward*200.0f);
        yield return new WaitForSecondsRealtime(3.5f);

        Sphere.velocity = Vector3.zero;

        Sphere.AddForce(Vector3.back*200.0f);
        yield return new WaitForSecondsRealtime(3.5f);

        Sphere.velocity = Vector3.zero;
        }
    }
}
