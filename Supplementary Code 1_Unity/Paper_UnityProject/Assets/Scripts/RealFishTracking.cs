using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

using System.Threading;

public class RealFishTracking : MonoBehaviour {
    public string listenIp = "127.0.0.1";
    public const int listenPort = 20486;
    private UdpReceiver udpReceiver;
    private Thread listenerThread;

    private float preXposition;
    private float preYposition;
    private float preZposition;

    private float NowXposition;
    private float NowYposition;
    private float NowZposition;
    private string Date = "20240102ZF999";

    // Save Data
    private string[] FrameGet;
    private string[] frameTimeRecordEx;
    private float frameTime;

    void Awake(){
        FrameGet = new string[0];
        frameTimeRecordEx = new string[0];
    }

    // Start is called before the first frame update
    void Start() {
        udpReceiver = new UdpReceiver(listenIp, listenPort);
        listenerThread = new Thread(udpReceiver.StartListener);
        listenerThread.Start();
    }

    // Update is called once per frame
    void Update() {

        Array.Resize<string>(ref FrameGet, FrameGet.Length + 1);
        FrameGet[FrameGet.Length-1] = udpReceiver.FrameStamp.ToString();
        frameTime = Time.time; Array.Resize<string>(ref frameTimeRecordEx, frameTimeRecordEx.Length + 1); frameTimeRecordEx[frameTimeRecordEx.Length-1] = frameTime.ToString();

        if(udpReceiver.Position.x > preXposition + 5.0f || udpReceiver.Position.x < preXposition - 5.0f){NowXposition = preXposition;}
        else{NowXposition = udpReceiver.Position.x;}

        //if(udpReceiver.Position.y > preYposition + 5.0f || udpReceiver.Position.y < preYposition - 5.0f){NowYposition = preYposition;}
        //else{NowYposition = udpReceiver.Position.y;}
        
        if(udpReceiver.Position.z > preZposition + 5.0f || udpReceiver.Position.z < preZposition - 5.0f){NowZposition = preZposition;}
        else{NowZposition = udpReceiver.Position.z;}

        transform.position = new Vector3((-NowXposition*1.75f), 10f,-NowZposition*1.75f+7.7f);
        //transform.rotation = Quaternion.AngleAxis(-udpReceiver.Yaw+90, Vector3.up);

        preXposition = NowXposition;
        preYposition = NowYposition;
        preZposition = NowZposition;
        // PythonDataSave();
    }

    void OnGUI() {
        Rect rectObj=new Rect(40,10,200,400);
        GUIStyle style = new GUIStyle();
        style.alignment = TextAnchor.UpperLeft;
        // GUI.Box(rectObj,"# Package receive from: "+listenIp+':'+listenPort+" #\n"
        //               + "\n FrameStamp  :"+ udpReceiver.FrameStamp
        //               + "\n FishCoor    :"+ udpReceiver.Position.ToString()
        //               + "\n FishYawAngle:"+ udpReceiver.Yaw
        //               + "\n TxLatency   :"+ udpReceiver.Latency + " ms"
        //         ,style);
    }

    void OnApplicationQuit() {
        listenerThread.Abort();
    }

    void PythonDataSave(){
        System.IO.File.WriteAllLines(Date + " PythonFrameRecord.txt", FrameGet);
        System.IO.File.WriteAllLines(Date + "FrameTimeRecordEx.txt", frameTimeRecordEx);
    }
}
