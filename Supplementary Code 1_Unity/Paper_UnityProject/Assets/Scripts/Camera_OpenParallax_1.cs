using UnityEngine;
using System.Collections.Generic;
using System.Globalization;

public class Camera_OpenParallax_1 : MonoBehaviour
{
    private List<Vector2> nosePositions = new List<Vector2>();
    private int currentIdx = 0;

    // Set before Exp
    private string Date = "20241120_T1_OP_";
    private float ExpTime = 1200.0f;
    private float BaselineTime = 300.0f;


    // Define the range of the camera's z-position.
    public const float minZ = -7.675f+17f;
    public const float maxZ = 7.675f+17f;

    // Define the range of lens shift values.
    public const float minLensShift = -0.48f;
    public const float maxLensShift = 0.48f;

    // Start is called before the first frame update
    void Start()
    {
        LoadCSV("02 二 2024 WT_vFFemale_Female_T3_posesSid.csv"); // Adjust the path as needed
    }

    void LoadCSV(string filePath)
    {
        // Read all lines from the CSV file
        string[] lines = System.IO.File.ReadAllLines(filePath);
        
        // Parse each line, starting from index 1 to skip the header
        for (int i = 1; i < lines.Length; i++)
        {
            string[] values = lines[i].Split(',');
            // Assuming 'NoseX' is at index 1 and 'NoseY' at index 2
            if (float.TryParse(values[1], NumberStyles.Any, CultureInfo.InvariantCulture, out float noseX) &&
                float.TryParse(values[2], NumberStyles.Any, CultureInfo.InvariantCulture, out float noseY))
            {
                nosePositions.Add(new Vector2(noseX, noseY));
            }
        }
    }

    // Update is called once per frame
    void Update()
    {
        if(Time.time > BaselineTime && Time.time < ExpTime){
            if (nosePositions.Count > 0)
            {
                // Get the current position from the list based on currentIdx
                Vector2 currentPosition = nosePositions[currentIdx];
                
                // Update the camera position. Modify this line as needed for your use case
                transform.position = new Vector3(-9f, 6.5f, -currentPosition.x/30+8f+17f);

                // Increment the index to move to the next position on the next frame
                currentIdx++;
                
                // Loop back to the start if we reach the end
                if (currentIdx >= nosePositions.Count)
                {
                    currentIdx = 0;
                }

                // Clamp the z-position within the defined range to avoid exceeding the expected lens shift values.
                float clampedZ = Mathf.Clamp(transform.position.z, minZ, maxZ);

                // Map the camera's z-position to the lens shift range.
                // Calculate the interpolation factor based on the position within the range.
                float t = (clampedZ - minZ) / (maxZ - minZ);

                // Interpolate the lens shift value based on the calculated factor.
                float lensShiftValue = Mathf.Lerp(minLensShift, maxLensShift, t);
                // float lensShiftValue = maxLensShift / maxZ * transform.position.z;

                // Apply the calculated lens shift value to the camera.
                GetComponent<Camera>().lensShift = new Vector2(lensShiftValue, 0); // Assumes shifting horizontally only.
            }
        }
    }
}
