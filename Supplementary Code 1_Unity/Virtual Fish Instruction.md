# Running Virtual Zebrafish

This guidence contains the information of steps to run the virtual zebrafish, including:
 1. File and Folder list
 2. Software list
 3. Steps to run Camera
 4. Steps to run Unity Project


## File and Folder in use
 1. CameraControl:
    - Configuration File: config.yml
    - DeepLabCut Model: ResNet50_batch2
    - Camera Control Python Folder: RealFishTracking
 2. Unity Project


## Software list
 1. Unity:
    - Unity Hub: 3.3.0

## Steps for Running Virtual Zebrafish
---
### Steps to run Camera

Open `config.yml`, and change `CameraSerialNum` to the camera serial number of each camera. Save the file after all changes are done.

**Recommended**: Change `Date`, `Task`, and `MaximumFrameNumber` if needed.
    1. `Date` and `Task` compose the file name. If these are not changed, the previous files will be covered.
    2. `MaximumFrameNumber` control the experiment time(baseline + testing time). 
        MaximumFrameNumber / framerate(30 frame per sec) = experiment time(sec).

Open Terminal, enter the three commands sequentially:

    cd CameraControl
    conda activate RealFishTracking
    python -m RealFishTracking

The windows showing the real fish(with deeplabcut tracking) will appear.

---
### Steps to run Unity Project

Install Unity Hub from internet.

Open Unity Project by Unity Hub.

Check the tick box of all the objects and scripts that are needed.

**Recommended**: `Date`, `ExpTime`, `BaselineTime` should be adjusted in the scripts controlling virtual zebrafish.

Click the start button.
