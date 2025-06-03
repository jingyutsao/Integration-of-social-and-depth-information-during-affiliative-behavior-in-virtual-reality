using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class OrientSwim : MonoBehaviour
{   
    System.Random rnd = new System.Random();

    // Range Setting
    private float xMaxWall = 35.0f;private float  xMinWall = 0.75f;
    private float YMaxWall = 25f;private float  YMinWall = 1.0f;
    private float ZMaxWall = 7.3f;private float  ZMinWall = -7.3f;
    private float HeadToCentroid = 1.0f;
    private float xMax; private float xMin;
    private float YMax; private float YMin;
    private float ZMax; private float ZMin;

    // Set before Exp
    private string Date = "20241124_T1_para";
    private float ExpTime = 1200.0f;
    private float BaselineTime = 0.0f;
    private float SwipingStart = 0.0f;
    private float SwipingEnd = 0.0f;
    private bool twoD = true;
    private bool Schooling = true; private double prob = 80;
    private bool FixedMotifSpeed = false;

    // Motif information receive
    private string filePath = "MotifInfoCompany_0731.csv";
    private int glideForceIndex;
    private int rotateTimeIndex;
    private int GlideDistancePlusIndex;
    private int glideTimeIndex;
    private int EventMinIndex;
    private int EventMaxIndex;
    private int vzIndex;
    private int vxIndex;
    private int VideoHeadDirectionIndex;
    private int AnimationHeadIndex;

    private string[,] data;
    private string AnimationTrig;
    private float AnimationHead;

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
    private int SwipCnt = 0;
    private float motifSpeed;

    // Num Setting
    private int i;
    private int EventMax;
    private int EventMin;
    
    // Time control
    private float RotateTime;
    private float GlideTime;
    private float elapsed = 0.0f;
    private float CurrentTime;
    private float lastTime;

    // Force control 
    private float GlideForce;

    // Distance calculation
    private float GlideDistancePlus;
    private float Predictdistance;
    private float Sidedistance;
    private float Fordictdistance;
    private float AdjustDistance;
    private float EndPositionX;
    private float EndPositionY;
    private float EndPositionZ;
    private Vector3 lastPosition = Vector3.zero;

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

    // Vertical rotation
    private float HeadAngleV;
    private float HeadAngleVCal;
    private float PositionY;
    private int k;
    private bool VertialCollision = true;
    private int VerSwim = 0;
    private bool Vertical;

    // Vector3 
    private Vector3 Forwall;
    private Vector3 Sidewall;
    private Vector3 SwipStart;
    private Vector3 relativePos;
    private Vector3 CurrentPosition;    
    private Vector3 EndPosition;

    // Judge parameters
    private int Swimstep = 0;  
    private bool isProgrammmingRun = true;
    private bool collisiondetect = true;

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
        Vzfx= new string[0]; Vzfy = new string[0]; Vzfz= new string[0]; HeadAngleSave= new string[0]; Forwardforce= new string[0]; frameTimeRecord= new string[0]; SwimScript= new string[0]; 
        
        /// Read Motif information
        string[] lines = System.IO.File.ReadAllLines(filePath);
        int rowCount = lines.Length;
        string[] header = lines[0].Split(',');
        int columnCount = header.Length;

        data = new string[rowCount, columnCount];

        for (int i = 0; i < rowCount; i++)
        {
            string[] values = lines[i].Split(',');

            for (int j = 0; j < columnCount; j++)
            {
                data[i, j] = values[j];
            }
        }

        System.IO.StreamReader reader = new System.IO.StreamReader(filePath);
        // Read the header line and split it into column names
        string headerLine = reader.ReadLine();
        string[] columnNames = headerLine.Split(',');

        // Find the indexes of the desired columns
        AnimationHeadIndex = Array.IndexOf(columnNames, "HeadAngle");
        glideForceIndex = Array.IndexOf(columnNames, "GlideForce");
        rotateTimeIndex = Array.IndexOf(columnNames, "RotateTime");
        GlideDistancePlusIndex = Array.IndexOf(columnNames, "GlideDistancePlus");
        glideTimeIndex = Array.IndexOf(columnNames, "GlideTime");
        EventMinIndex = Array.IndexOf(columnNames, "EventMin");
        EventMaxIndex = Array.IndexOf(columnNames, "EventMax");
        vxIndex = Array.IndexOf(columnNames, "Vx");
        vzIndex = Array.IndexOf(columnNames, "Vz");
        VideoHeadDirectionIndex = Array.IndexOf(columnNames, "VideoHeadDirection");
        
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
         //transform.position = new Vector3(3f, 9.25f, 0.0f);
         //transform.rotation = Quaternion.Euler(new Vector3(0f, 45f, 0.0f));
        transform.position = new Vector3(17.85f, 9.25f, 0.0f);
        print("Start swim " + Time.time);
       
    while(isProgrammmingRun == true){

        // Spontaneous
        if(Swimstep == 0){
            
            MovementGet = new float[0];
            k = rnd.Next(0,20); // 3D swim

        // Collision prevention (horizontal)
        for(HeadAngle = -180.0f; HeadAngle <= 185.0f; HeadAngle += 10){
            if(HeadAngle == 0){i=rnd.Next(-2,2); HeadAngle+=i;}
            ReadMotif();

            Degree = transform.rotation.eulerAngles.y + HeadAngle;
            if ((Degree >= 70 && Degree <= 110) || (Degree >= 250 && Degree <= 290)){
                xMax = xMaxWall - HeadToCentroid; xMin = xMinWall + HeadToCentroid; 
                YMax = YMaxWall; YMin = YMinWall;
                ZMax = ZMaxWall; ZMin = ZMinWall;
            }
            else if ((Degree >= 340 && Degree <= 20) || (Degree >= 160 && Degree <= 200)){
                xMax = xMaxWall; xMin = xMinWall;
                YMax = YMaxWall; YMin = YMinWall;
                ZMax = ZMaxWall - HeadToCentroid; ZMin = ZMinWall + HeadToCentroid;
            }
            else {
                xMax = xMaxWall - HeadToCentroid; xMin = xMinWall + HeadToCentroid;
                YMax = YMaxWall; YMin = YMinWall;
                ZMax = ZMaxWall - HeadToCentroid; ZMin = ZMinWall + HeadToCentroid;
            }

            CollisionAvoid(); 

            // print the position of virtual fish for checking(not necessary)
            string InRange = String.Format("NextPosition.x = {0}, NextPosition.z = {1}, xMin = {2}, xMax = {3}, zMin = {4}, zMax = {5}, EndPositionX = {6}, {7}, EndPositionZ = {8}, {9}, HeadAngle = {10}", 
            NextPosition.x, NextPosition.z, NextPosition.x>= xMin, NextPosition.x<= xMax, NextPosition.z>= ZMin, NextPosition.z<= ZMax, EndPositionX >= (xMin + 1.5f), EndPositionX <= (xMax - 1.5f), EndPositionZ >= (ZMin + 1.0f), EndPositionZ <= (ZMax - 1.0f), AnimationHead);
            // print(InRange);

            collisiondetect = true;

            // collision detect and the edge is set more inside
            if(EndPositionX >= (xMin + 2.0f) && EndPositionX <= (xMax - 2.0f) && EndPositionZ >= (ZMin + 1.5f) && EndPositionZ <= (ZMax - 1.5f)
                && NextPosition.x>= xMin && NextPosition.x>= xMin 
                && NextPosition.z>= ZMin  && NextPosition.z<= ZMax){
            collisiondetect = false;

            }

            if(collisiondetect == false){
                for(int j = EventMin; j <= EventMax; j++){
                    Array.Resize<float>(ref MovementGet, MovementGet.Length + 1);
                    MovementGet[MovementGet.Length-1] = AnimationHead;
                }
                    collisiondetect = true;
            }

        }
            
            // Collision prevention (vertical)
            if (transform.position.y <= (YMin + 3.0f)){HeadAngleV = UnityEngine.Random.Range(0.0f,30.0f);} // if virtual fish's position is too high or too low
            else if (transform.position.y >= (YMax - 3.0f)){HeadAngleV = UnityEngine.Random.Range(-30.0f,0.0f);}
            else{HeadAngleV = UnityEngine.Random.Range(-30.0f,30.0f);}                
            
            HeadAngle = 0.0f;
            ReadMotif();

            Degree = transform.rotation.eulerAngles.y + HeadAngle;
            if ((Degree >= 70 && Degree <= 110) || (Degree >= 250 && Degree <= 290)){
                xMax = xMaxWall - HeadToCentroid; xMin = xMinWall + HeadToCentroid; 
                YMax = YMaxWall; YMin = YMinWall;
                ZMax = ZMaxWall; ZMin = ZMinWall;
            }
            else if ((Degree >= 340 && Degree <= 20) || (Degree >= 160 && Degree <= 200)){
                xMax = xMaxWall; xMin = xMinWall;
                YMax = YMaxWall; YMin = YMinWall;
                ZMax = ZMaxWall - HeadToCentroid; ZMin = ZMinWall + HeadToCentroid;
            }
            else {
                xMax = xMaxWall - HeadToCentroid; xMin = xMinWall + HeadToCentroid;
                YMax = YMaxWall; YMin = YMinWall;
                ZMax = ZMaxWall - HeadToCentroid; ZMin = ZMinWall + HeadToCentroid;
            }

            CollisionAvoid();

            collisiondetect = true; 

            if(EndPositionX >= (xMin + 2.0f) && EndPositionX <= (xMax - 2.0f)
                && EndPositionZ >= (ZMin + 1.5f) && EndPositionZ <= (ZMax - 1.5f)
                && EndPositionY >= (YMin + 1.0f) && EndPositionY <= (YMax - 1.0f)
                && twoD != true){
                collisiondetect = false;
                VertialCollision = false;
            }

            

            /// Spontaneous swim start
            // Rotation (horizontal)
            if(VertialCollision == true || VerSwim >=7 || k<=10 || HeadAngleV == 0){
                // Get motif
                Vertical = false;
                randomNum = rnd.Next(0,100); 
                if(Schooling == true && randomNum <= prob){
                    CertainDirection();
                    HeadAngle = RelativeAngle;
                }
                else{
                    i = rnd.Next(0,MovementGet.Length-1); 
                    HeadAngle = MovementGet[i];                    
                }

                Array.Resize<string>(ref HeadAngleSave, HeadAngleSave.Length + 1); HeadAngleSave[HeadAngleSave.Length-1] = HeadAngle.ToString();
                
                float SwimstepSpon = 1.1f;
                Array.Resize<string>(ref SwimScript, SwimScript.Length + 1); SwimScript[SwimScript.Length-1] = SwimstepSpon.ToString();
                GetTargetSpeed();
                ReadMotif(); TailBend();
                
                targetHeading = transform.rotation * Quaternion.Euler(Vector3.up * HeadAngle);

                AngleCal();
                
                FutureMoveAngle = CosAngle - VideoHeadDirection;

                float cosang = Mathf.Cos(FutureMoveAngle*Mathf.Deg2Rad);
                float sinang = Mathf.Sin(FutureMoveAngle*Mathf.Deg2Rad);

                VzN = Vz*cosang - Vx*sinang;
                VxN = Vz*sinang + Vx*cosang;

                NextPosition = new Vector3(transform.position.x+VxN, transform.position.y, transform.position.z+VzN);

                xMax = xMaxWall - HeadToCentroid; xMin = xMinWall + HeadToCentroid;
                YMax = YMaxWall; YMin = YMinWall;
                ZMax = ZMaxWall - HeadToCentroid; ZMin = ZMinWall + HeadToCentroid;

                CurrentDirection = transform.rotation;
                CurrentPosition = transform.position;

                elapsed = 0.0f;
                while(elapsed < RotateTime){
                    transform.rotation = Quaternion.Slerp(CurrentDirection, targetHeading, elapsed/RotateTime);
                    transform.position = Vector3.Lerp(CurrentPosition, NextPosition, elapsed/RotateTime);

                    transform.position = new Vector3(
                        Mathf.Clamp(transform.position.x, xMin, xMax), 
                        Mathf.Clamp(transform.position.y, YMin, YMax), 
                        Mathf.Clamp(transform.position.z, ZMin, ZMax)
                    );

                    elapsed += Time.deltaTime;
                    yield return null;
                 }

                transform.rotation = targetHeading;
                transform.position = NextPosition;
                VerSwim -= 1;
            
            }


            // Rotation (vertical)
            if(VertialCollision == false && VerSwim < 7 && k > 10 &&  HeadAngleV != 0){
                Vertical = true;
                HeadAngle = 0.0f;
                GetTargetSpeed();
                ReadMotif(); TailBend();
                float SwimstepSpon = 1.2f;
                Array.Resize<string>(ref SwimScript, SwimScript.Length + 1); SwimScript[SwimScript.Length-1] = SwimstepSpon.ToString();

                elapsed = 0.0f;
                RotateTime = 0.06f;
                Array.Resize<string>(ref HeadAngleSave, HeadAngleSave.Length + 1); HeadAngleSave[HeadAngleSave.Length-1] = HeadAngleV.ToString();

                while(elapsed < RotateTime){
                    transform.Rotate(Vector3.right, HeadAngleV*(elapsed/RotateTime), Space.Self); 
                    elapsed += Time.fixedDeltaTime;
                    VirtualFish.angularVelocity = Vector3.zero;
                    yield return null;
                }

                if(HeadAngleV>=0.0f){
                transform.rotation = Quaternion.Euler(new Vector3(HeadAngleV,transform.rotation.eulerAngles.y,0.0f)); 
                }       

                else{
                transform.rotation = Quaternion.Euler(new Vector3((360.0f + HeadAngleV),transform.rotation.eulerAngles.y,0.0f));
                }

            }

            CurrentTime = Time.time;

            if (Vertical == true){
                EndPosition = new Vector3(
                    transform.position.x + (GlideDistancePlus - 1) * (Mathf.Cos((((Degree - 270)*(-1))*Mathf.Deg2Rad))), 
                    transform.position.y + (GlideDistancePlus - 1) * Mathf.Tan(HeadAngleV*Mathf.Deg2Rad), 
                    transform.position.z + (GlideDistancePlus - 1) * (Mathf.Sin((((Degree - 270)*(-1))*Mathf.Deg2Rad))));
            }
            else{
                EndPosition = new Vector3(
                    transform.position.x + (GlideDistancePlus - 1) * (Mathf.Cos((((Degree - 270)*(-1))*Mathf.Deg2Rad))), 
                    transform.position.y, 
                    transform.position.z + (GlideDistancePlus - 1) * (Mathf.Sin((((Degree - 270)*(-1))*Mathf.Deg2Rad))));
            }

            //Move forward

            // Acceleration
            float GlideDistance = GlideDistancePlus - 1f; // distance
            float v = 1.5f;
            float v0 = (2 * GlideDistance - v*GlideTime) / GlideTime;
            float a = (v - v0) / GlideTime;
            // float a = -2 * GlideDistance / (GlideTime * GlideTime); // Let V1 = 0, a = (2s - 2V0t)/t**2
            // float v0 = (GlideDistance/GlideTime) - (0.5f * a * GlideTime);

            float t = 0f;
            float distanceTravelled = 0f;
            
            while(Time.time < CurrentTime + GlideTime){
                // Acceleration
                float distanceAccumulation = v0 * t + 0.5f * a * t * t; // s = v0t + (1/2)a(t**2)
                float distancePerTime = distanceAccumulation - distanceTravelled;
                transform.position = Vector3.MoveTowards(transform.position, EndPosition, distancePerTime);

                // transform.position = Vector3.MoveTowards(transform.position, EndPosition, (GlideDistancePlus - 1)/(GlideTime/Time.deltaTime));
                transform.position = new Vector3(
                Mathf.Clamp(transform.position.x, xMin, xMax), 
                Mathf.Clamp(transform.position.y, YMin, YMax), 
                Mathf.Clamp(transform.position.z, ZMin, ZMax)
                );
                // Acceleration
                t += Time.deltaTime;
                distanceTravelled += distancePerTime;
                yield return null;
            }

            Array.Resize<string>(ref Forwardforce, Forwardforce.Length + 1); Forwardforce[Forwardforce.Length-1] = GlideForce.ToString();
            
            // Rotation back (vertical)
            if(Vertical == true){
  
                HeadAngle = 0.0f;
                GetTargetSpeed();
                ReadMotif(); TailBend();

                 elapsed = 0.0f;
                 RotateTime = 0.06f;

                while(elapsed < RotateTime){
                    transform.Rotate(Vector3.right, -HeadAngleV*(elapsed/RotateTime), Space.Self); 
                    elapsed += Time.fixedDeltaTime;
                    VirtualFish.angularVelocity = Vector3.zero;
                    yield return null;
                }  
                transform.rotation = Quaternion.Euler(new Vector3(0.0f,transform.rotation.eulerAngles.y,0.0f));  

                VertialCollision = true;
                VerSwim += 3;
                
            }

            mAnimator.SetFloat("AnimationTrigger", -1.0f);
            yield return null;
            
            // Time control
            // Update behavior mode with time
            if(Time.time > SwipingStart && Time.time < SwipingEnd){print("The time swiping start: " + Time.time); OnApplicationQuit();}

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
    
    }

    
    // Each Exp. part switch
    void OnApplicationQuit(){

        // Quit swim
        if(Swimstep == 0 ){
            Swimstep = 1;
            Debug.Log("SwimStop");
        }

        // Quit swip
        else if(Swimstep == 1){
            Swimstep = 0;
            Debug.Log("SwipStop");            
        }         
    }
    
    /// Collision detection
    // ForWall distance calculation
    private void CollisionAvoid(){

            AngleCal();

            // 0 - 45
            if(Degree >= 0.0f && Degree <= 45.0f){
                Forwall = new Vector3(transform.position.x, transform.position.y, ZMin);
                Sidewall = new Vector3(xMin, transform.position.y, transform.position.z);
                DegreeCal = Degree;
                } 

            // 45 - 90
            else if(Degree > 45.0f && Degree <= 90.0f){
                Forwall = new Vector3(xMin, transform.position.y, transform.position.z);
                Sidewall = new Vector3(transform.position.x, transform.position.y, ZMin);
                DegreeCal = 90.0f - Degree;
            }

            // 90 - 135
            else if(Degree > 90.0f && Degree <= 135.0f){
                Forwall = new Vector3(xMin, transform.position.y, transform.position.z);
                Sidewall = new Vector3(transform.position.x, transform.position.y, ZMax);
                DegreeCal = Degree - 90.0f;
            }

            // 135 - 180
            else if(Degree > 135.0f && Degree <= 180.0f){
                Forwall = new Vector3(transform.position.x, transform.position.y, ZMax);
                Sidewall = new Vector3(xMin, transform.position.y, transform.position.z);
                DegreeCal = 180.0f - Degree;
            }

            // 180 - 225
            else if(Degree > 180.0f && Degree <= 225.0f){
                Forwall = new Vector3(transform.position.x, transform.position.y, ZMax);
                Sidewall = new Vector3(xMax, transform.position.y, transform.position.z);
                DegreeCal = Degree - 180.0f;
            }

            // 225 - 270
            else if(Degree > 225.0f && Degree <= 270.0f){
                Forwall = new Vector3(xMax, transform.position.y, transform.position.z);
                Sidewall = new Vector3(transform.position.x, transform.position.y, ZMax);
                DegreeCal = 270.0f - Degree;
            }

            // 270 - 315
            else if(Degree > 270.0f && Degree <= 315.0f){
                Forwall = new Vector3(xMax, transform.position.y, transform.position.z);
                Sidewall = new Vector3(transform.position.x, transform.position.y, ZMin);
                DegreeCal = Degree - 270.0f;
            }

            // 315 - 360
            else if(Degree > 315.0f && Degree <= 360.0f){
                Forwall = new Vector3(transform.position.x, transform.position.y, ZMin);
                Sidewall = new Vector3(xMax, transform.position.y, transform.position.z);
                DegreeCal = 360.0f - Degree;
            } 

            DistanceCal();
    }

    // Angle calculation
    private void AngleCal(){
        
        // Get current angle
        CosAngle = transform.rotation.eulerAngles.y;

        // Calculate future angle
        Degree = CosAngle + HeadAngle;
        FutureMoveAngle = CosAngle - VideoHeadDirection;
        
        if(Degree < 0){Degree = 360.0f + Degree;}
        else if(Degree > 360.0f){Degree = Degree - 360.0f;}
    }

    // Collision calcaulate distance (Horizontal)
    private void DistanceCal(){

        // Get the next position after rotation
        float cosang = Mathf.Cos(FutureMoveAngle*Mathf.Deg2Rad);
        float sinang = Mathf.Sin(FutureMoveAngle*Mathf.Deg2Rad);

        VzN = Vz*cosang - Vx*sinang;
        VxN = Vz*sinang + Vx*cosang;

        if (HeadAngleV == 0){
            NextPosition = new Vector3(transform.position.x+VxN, transform.position.y, transform.position.z+VzN);
        }
        else{
            NextPosition = new Vector3(transform.position.x, transform.position.y, transform.position.z);
        }
        
        DegreeCal = DegreeCal*Mathf.Deg2Rad;

        // caculate the end point of a movement
        EndPositionX = NextPosition.x + GlideDistancePlus* (Mathf.Cos((((Degree - 270)*(-1))*Mathf.Deg2Rad)));
        EndPositionY = NextPosition.y + GlideDistancePlus* (Mathf.Tan(HeadAngleVCal*Mathf.Deg2Rad));
        EndPositionZ = NextPosition.z + GlideDistancePlus* (Mathf.Sin((((Degree - 270)*(-1))*Mathf.Deg2Rad)));

        // The distance between two Forwalls(for swiping)
        Sidedistance = Vector3.Distance(NextPosition, Sidewall);
        Fordictdistance = Vector3.Distance(NextPosition, Forwall);

        // detect collision(for swiping)
        AdjustDistance = Fordictdistance * (Mathf.Tan(DegreeCal));
        if(Sidedistance >= AdjustDistance){Predictdistance = (Fordictdistance / (Mathf.Cos(DegreeCal)));}
        else{Predictdistance = (Sidedistance/ (Mathf.Sin(DegreeCal)));}

    }

    private void ReadMotif(){   

        if(HeadAngle < -180){HeadAngle = -180.0f;}
        if(HeadAngle > 180){HeadAngle = 180.0f;}
        
        if (HeadAngle < 0.0f)
        {
            idx = Convert.ToInt32(Mathf.Abs(HeadAngle / 10.0f)) + 1;
        }
        else
        {
            idx = Convert.ToInt32(Mathf.Abs(HeadAngle / 10.0f)) + 20;
        }

        AnimationHead = int.Parse(data[idx, AnimationHeadIndex]); 
        GlideForce = float.Parse(data[idx, glideForceIndex]); 
        RotateTime = float.Parse(data[idx, rotateTimeIndex]);
        GlideDistancePlus = float.Parse(data[idx, GlideDistancePlusIndex]);
        GlideTime = float.Parse(data[idx, glideTimeIndex]); 
        EventMin = int.Parse(data[idx, EventMinIndex]); 
        EventMax = int.Parse(data[idx, EventMaxIndex]);
        Vx = float.Parse(data[idx, vxIndex]); 
        Vz = float.Parse(data[idx, vzIndex]); 
        VideoHeadDirection = float.Parse(data[idx, VideoHeadDirectionIndex]);

        RotateTime = RotateTime / motifSpeed;
        GlideTime = GlideTime / motifSpeed;
    }
    

    // Tail bend animation
    private void TailBend(){

        if(mAnimator != null)
        {   
            AnimationHead = int.Parse(data[idx, AnimationHeadIndex]);
            if(AnimationHead == 0 && int.Parse(data[idx, AnimationHeadIndex]) <= 0){
                AnimationHead = -5.0f;
            }

            if(AnimationHead == 0 && int.Parse(data[idx, AnimationHeadIndex]) > 0){
                AnimationHead = 5.0f;
            }

            mAnimator.SetFloat("AnimationTrigger", 1.0f);
            mAnimator.SetFloat("AnimationSpeed", motifSpeed);
            mAnimator.SetFloat("HeadAngle", AnimationHead);
        }
    }

    void SaveVirtualFishData(){
        string csvFilePath = Date + "Data.csv"; // Specify the path and name of the CSV file

        // Define the header row
        string[] PerFrameheader = {"xAxis", "yAxis", "zAxis", "FrameTimeRecord" };
        string[] Swimheader = {"HeadAngle", "SwipGlideForce",  "SwimScript" };

        // Combine the data from different arrays into a jagged array
        string[][] PerFramedataRows = new string[Vzfx.Length][];
        string[][] SwimdataRows = new string[HeadAngleSave.Length][];


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

        for (int i = 0; i < HeadAngleSave.Length; i++)
        {
        SwimdataRows[i] = new string[]
            {
                HeadAngleSave[i],
                Forwardforce[i],
                SwimScript[i]
            };
        }

        // Create a list to store all the lines in the CSV file
        List<string> PerFramecsvLines = new List<string>();
        List<string> SwimcsvLines = new List<string>();

        // Add the header row to the list
        PerFramecsvLines.Add(string.Join(",", PerFrameheader));
        SwimcsvLines.Add(string.Join(",", Swimheader));

        // Add the data rows to the list
        foreach (string[] row in PerFramedataRows)
        {
            PerFramecsvLines.Add(string.Join(",", row));
        }

        foreach (string[] row in SwimdataRows)
        {
            SwimcsvLines.Add(string.Join(",", row));
        }

        // Write the CSV lines to the file
        System.IO.File.WriteAllLines("PerFrame" + csvFilePath, PerFramecsvLines);
        System.IO.File.WriteAllLines("Swim" + csvFilePath, SwimcsvLines);

    }

    private void CertainDirection(){

        Vector3 DirectionVector = SchoolingTarget.position - transform.position;

        float radiant = Mathf.Atan2(DirectionVector.x, DirectionVector.z);

        orientation = radiant * Mathf.Rad2Deg;

        orientation = (orientation + 180) % 360;
        // print("orientation: " + orientation);
        
        // Calculate the relative angle
        RelativeAngle =  orientation - transform.rotation.eulerAngles.y;

        if (RelativeAngle > 180)
            RelativeAngle -= 360;
        else if (RelativeAngle < -180)
            RelativeAngle += 360;
    }

    private void GetTargetSpeed(){
        float TargetSpeed = Vector3.Distance(SchoolingTarget.position, lastPosition) / ((Time.time - lastTime)*2);
        lastPosition = SchoolingTarget.position;
        lastTime = Time.time;
        if(TargetSpeed <= 1f || FixedMotifSpeed == true){motifSpeed = 1f;}
        else{motifSpeed = TargetSpeed*0.5f;}
        
    }

}

