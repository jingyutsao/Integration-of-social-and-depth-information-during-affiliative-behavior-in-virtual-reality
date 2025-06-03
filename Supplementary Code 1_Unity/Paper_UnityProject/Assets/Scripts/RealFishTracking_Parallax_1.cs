using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

using System.Threading;

public class RealFishTracking_Parallax_1 : MonoBehaviour {

    // Set before Exp
    private string Date = "20241205_T4_para_";
    private float ExpTime = 1200.0f;
    private float BaselineTime = 300.0f;

    public string listenIp = "127.0.0.1";
    public const int listenPort = 20487;
    private UdpReceiver udpReceiver;
    private Thread listenerThread;

    private float preXposition;
    private float preYposition;
    private float preZposition;

    private float NowXposition;
    private float NowYposition;
    private float NowZposition;

    private Camera camera;

    // Define the range of the camera's z-position.
    public const float minZ = -7.675f+17f;
    public const float maxZ = 7.675f+17f;

    // Define the range of lens shift values.
    public const float minLensShift = -0.48f; //-0.48
    public const float maxLensShift = 0.48f; //0.48

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

        camera = GetComponent<Camera>();
    }

    // Update is called once per frame
    void Update() {
        if(Time.time > BaselineTime && Time.time < ExpTime){

            Array.Resize<string>(ref FrameGet, FrameGet.Length + 1);
            FrameGet[FrameGet.Length-1] = udpReceiver.FrameStamp.ToString();
            frameTime = Time.time; Array.Resize<string>(ref frameTimeRecordEx, frameTimeRecordEx.Length + 1); frameTimeRecordEx[frameTimeRecordEx.Length-1] = frameTime.ToString();

            if(udpReceiver.Position.x > preXposition + 5.0f || udpReceiver.Position.x < preXposition - 5.0f){NowXposition = preXposition;}
            else{NowXposition = udpReceiver.Position.x;}

            //if(udpReceiver.Position.y > preYposition + 5.0f || udpReceiver.Position.y < preYposition - 5.0f){NowYposition = preYposition;}
            //else{NowYposition = udpReceiver.Position.y;}
            
            if(udpReceiver.Position.z > preZposition + 5.0f || udpReceiver.Position.z < preZposition - 5.0f){NowZposition = preZposition;}
            else{NowZposition = udpReceiver.Position.z;}

            transform.position = new Vector3(-9f, 6.5f,-NowZposition*1.75f+7.7f+16.2f);
             //transform.position = new Vector3(-9f, 6.5f,-(-NowZposition*1.75f+7.7f)+16.2f); //Negative parallax
            //transform.position = new Vector3((-NowXposition*1.75f), 6.5f,-NowZposition*1.75f+7.7f+16.2f);
            //transform.rotation = Quaternion.AngleAxis(-udpReceiver.Yaw+90, Vector3.up);

            preXposition = NowXposition;
            preYposition = NowYposition;
            preZposition = NowZposition;

            // Clamp the z-position within the defined range to avoid exceeding the expected lens shift values.
            float clampedZ = Mathf.Clamp(transform.position.z, minZ, maxZ);

            // Map the camera's z-position to the lens shift range.
            // Calculate the interpolation factor based on the position within the range.
            float t = (clampedZ - minZ) / (maxZ - minZ);

            // Interpolate the lens shift value based on the calculated factor.
            float lensShiftValue = Mathf.Lerp(minLensShift, maxLensShift, t);

            // Apply the calculated lens shift value to the camera.
            camera.lensShift = new Vector2(lensShiftValue, 0); // Assumes shifting horizontally only.

            PythonDataSave();

        }
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
        System.IO.File.WriteAllLines(Date + " PythonFrameRecord_1.txt", FrameGet);
        System.IO.File.WriteAllLines(Date + "FrameTimeRecordEx_1.txt", frameTimeRecordEx);
    }
}
