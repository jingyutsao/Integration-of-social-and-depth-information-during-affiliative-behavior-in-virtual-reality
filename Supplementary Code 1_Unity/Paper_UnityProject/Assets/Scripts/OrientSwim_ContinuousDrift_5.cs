using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class OrientSwim_ContinuousDrift_5 : MonoBehaviour
{   
    System.Random rnd = new System.Random();

    // Range Setting
    private float xMaxWall = 35.0f;private float  xMinWall = 0.75f;
    private float YMaxWall = 25f;private float  YMinWall = 1.0f;
    private float ZMaxWall = 7.3f + 17f;private float  ZMinWall = -7.3f + 17f;
    private float xMax; private float xMin;
    private float YMax; private float YMin;
    private float ZMax; private float ZMin;

    // Set before Exp
    private string Date = "20241013_T1_para";
    private float ExpTime = 1200.0f;
    private float BaselineTime = 300.0f;

    // Variable for Move position during Rotate
    private float Vx;
    private float Vz;
    private Vector3 NextPosition;
    private float VideoHeadDirection;
    private float FutureMoveAngle;
    private int Frame;
    private float VxN;
    private float VzN;
    private int idx;
    private float orientation;
    private float RelativeAngle;
    private float randomNum;

    private string[] MotifGet;

    // Set object parameters
    private Animator mAnimator;
    private Rigidbody VirtualFish;
    private Transform Sphere;
    private Transform SchoolingTarget;
    
    // Time control
    private float RotateTime;
    private float GlideTime;
    private float CurrentTime;
    private float lastTime;


    // Angle parameters
    private Quaternion targetHeading;
    private Quaternion CurrentDirection;
    private float HeadAngle;
    private float HeadDirection;
    private float CosAngle;
    private float Degree;
    private float DegreeCal;
    private float DegPast;
    private float DegFuture;

    // Judge parameters
    private bool isProgrammmingRun = true;

    // Read Data
    private string[] Movement; private float[] MovementGet;

    // Save Data
    private string[] Vzfx;
    private string[] Vzfy;
    private string[] Vzfz;
    private string[] HeadAngleSave;
    private string[] Forwardforce;
    private string[] frameTimeRecord;
    private string[] SwimScript;
    private float xAxis;
    private float yAxis;
    private float zAxis;
    private float frameTime;

    // initialization
    void Awake(){

        /// Initiate the variables
        mAnimator = GetComponent<Animator>();
        VirtualFish = gameObject.GetComponent<Rigidbody>();
        Sphere = GameObject.Find("Sphere").GetComponent<Transform>();
        SchoolingTarget = GameObject.Find("Sphere (2)").GetComponent<Transform>();
        Vzfx= new string[0]; Vzfy = new string[0]; Vzfz= new string[0]; frameTimeRecord= new string[0]; 
    }

    // Start is called before the first frame update
    void Start(){
        StartCoroutine(Run()); 
    }


    // Update is called once per frame
    void Update(){

        //Limit the region
        if(Time.time > BaselineTime){
            transform.position = new Vector3(
                            Mathf.Clamp(transform.position.x, xMinWall, xMaxWall), 
                            Mathf.Clamp(transform.position.y, YMinWall, YMaxWall), 
                            Mathf.Clamp(transform.position.z, ZMinWall, ZMaxWall)
                        );
        }

        // Save Position and Time data
        xAxis = transform.position.x; Array.Resize<string>(ref Vzfx, Vzfx.Length + 1); Vzfx[Vzfx.Length-1] = xAxis.ToString();
        yAxis = transform.position.y; Array.Resize<string>(ref Vzfy, Vzfy.Length + 1); Vzfy[Vzfy.Length-1] = yAxis.ToString();
        zAxis = transform.position.z; Array.Resize<string>(ref Vzfz, Vzfz.Length + 1); Vzfz[Vzfz.Length-1] = zAxis.ToString();
        frameTime = Time.time; Array.Resize<string>(ref frameTimeRecord, frameTimeRecord.Length + 1); frameTimeRecord[frameTimeRecord.Length-1] = frameTime.ToString();
        
    }

    // Run Swimming Code
    IEnumerator Run(){
        
        // Initial condition
        yield return new WaitForSecondsRealtime(BaselineTime);
        VirtualFish.transform.Rotate(0.0f, -90.0f, 0.0f, Space.Self);
        transform.position = new Vector3(3.0f, 4.0f, 17.0f);
        print("Start swim " + Time.time);
        
        while(isProgrammmingRun == true){
            // VirtualFish.AddRelativeForce(Vector3.back*150.0f);
            // yield return new WaitForSecondsRealtime(3f);
            // VirtualFish.velocity = Vector3.zero;
            // VirtualFish.transform.Rotate(0.0f, 180.0f, 0.0f, Space.Self);
            while(Time.time < 2000.0f){
                VirtualFish.AddForce(Vector3.back*125.0f);
                yield return new WaitForSecondsRealtime(5.5f);
                VirtualFish.velocity = Vector3.zero;
                transform.position = new Vector3(3.0f, 4.0f, 23.0f);
            }        
            // Finish experiment
            if(Time.time >= ExpTime){
                print("Experiment " + Date + " is done."); 
                print("The time end " + Time.time); 
                SaveVirtualFishData();
                Application.Quit();
                break;
            }

        }

    }


    void SaveVirtualFishData(){
        string csvFilePath = Date + "Data_5.csv"; // Specify the path and name of the CSV file

        // Define the header row
        string[] PerFrameheader = {"xAxis", "yAxis", "zAxis", "FrameTimeRecord" };

        // Combine the data from different arrays into a jagged array
        string[][] PerFramedataRows = new string[Vzfx.Length][];


        for (int i = 0; i < Vzfx.Length; i++)
        {
        PerFramedataRows[i] = new string[]
            {
                Vzfx[i],
                Vzfy[i],
                Vzfz[i],
                frameTimeRecord[i],
            };
        }

        // Create a list to store all the lines in the CSV file
        List<string> PerFramecsvLines = new List<string>();

        // Add the header row to the list
        PerFramecsvLines.Add(string.Join(",", PerFrameheader));

        // Add the data rows to the list
        foreach (string[] row in PerFramedataRows)
        {
            PerFramecsvLines.Add(string.Join(",", row));
        }

        // Write the CSV lines to the file
        System.IO.File.WriteAllLines("PerFrame" + csvFilePath, PerFramecsvLines);

    }

}