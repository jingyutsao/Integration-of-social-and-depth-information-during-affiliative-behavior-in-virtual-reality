using UnityEngine;

using System;
using System.Text;
using System.Net;
using System.Net.Sockets;
using System.Threading;

public class UdpReceiver{
    public int FrameStamp{get{return frameStamp;}}
    public Vector3 Position{get{return position;}}
    public float Yaw{get{return yaw;}}
    public int Latency{get{return latency;}}

    private int frameStamp;
    private Vector3 position;
    private float yaw;
    private int latency;
    private UdpClient listener;
    private IPEndPoint localhostEP;
    private static char[] delimiterChars = {'[', ',', ']'};

    public UdpReceiver(string listenIp="127.0.0.1",int listenPort=20486){
        Debug.Log("Initialize UDP listener.");
        try{
            listener = new UdpClient(listenPort);
            localhostEP = new IPEndPoint(IPAddress.Parse(listenIp), listenPort);
        } catch (Exception e){
            Debug.Log(e);
        }
    }

    public void StartListener() {
        try {
            do {
                // Encoding.ASCII.GetString(bytes, 0, bytes.Length)
                byte[] bytes = listener.Receive(ref localhostEP);
                string msgRx = Encoding.UTF8.GetString(bytes);

                // split the received message
                string[] phraseWords = msgRx.Split(delimiterChars);

                // get the position and yaw information
                frameStamp = int.Parse(phraseWords[0]);
                float xCoor = float.Parse(phraseWords[1]);
                float yCoor = 5.88f;
                float zCoor = float.Parse(phraseWords[2]);
                position = new Vector3(xCoor, yCoor, zCoor);
                yaw = float.Parse(phraseWords[3]);
                
                // get the timing information
                long txTime = long.Parse(phraseWords[4])/1000000;
                long unixTime = ((DateTimeOffset)DateTime.Now).ToUnixTimeMilliseconds();
                latency = (int)(unixTime - txTime);
            } while(true);
        }
        catch (Exception e) {
            Debug.Log(e);
        }
        finally {
            listener.Close();
            Debug.Log("UDP listener stop.");
        }
    }
}