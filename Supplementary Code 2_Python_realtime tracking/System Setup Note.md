# Environment Setup for Running vZF Code

This guidence contains the information of setting up the environment to run the virtual zebrafish code, including:
 1. Hardware list
 2. Package list
 3. Operating system setup
 4. Installation of Nvdia GPU driver and CUDA toolkit
 5. Installation of Python, and setup the conda environment
 6. Installation of FLIR Spinnaker SDK
 7. Other useful services that is not related to the code

## Hardware in use
 - CPU: AMD R5 5600X
 - GPU: Nvidia RTX3070 w/ 8G VRAM
 - RAM: 32 GB DDR4-3200MHz

## Package list
 1. Operating System:
    - Distribution: Ubuntu 20.04.1
    - Linux Kernel: 5.13.0-48-generic
 2. Compilers:
    - gcc compiler v9.4.0
    - g++ compiler v9.4.0
 3. GPU Drivers & CUDA:
    - Nvidia driver: 515.43.04
    - CUDA Version: 11.7.64
    - cuDNN Version: 8.4.1.50
 4. FLIR Spinnaker:
    - Spinnaker SDK: 2.5.0.80
    - Python-Spinnaker: 2.5.0.80-cp37
 5. Python Essential Packages:
    - Python interpreter:3.7.12
    - Tensorflow: 2.7.3
    - DeepLabCut: 2.2.0.6
    - DeepLabCut-Live: 1.0.1
    - NumPy: 1.18.5
    - OpenCV: 4.6.0.66

## Operating system setup
---
### Update Operating System Packages

With the internet connected, now we can install the latest versions of all packages currently on the system. First, resynchronize the package index from their sources:

    sudo apt update

After refreshing the index, use the following command to upgrade those packages:

    sudo apt upgrade

---
### Install development essential toolkit

This toolkit include essential packages for a c/c++ project, which will be needed during the compilation of the wxPython

    sudo apt install build-essential

---
## Install GPU Drivers and CUDA Toolkits[^2]

### NVIDIA driver

If the option of "Install third-party software for graphics and ..." was checked during the installation of the OS. The GPU driver should already be installed into the system. Open the `Software & Updates` app and go to the `Additional Drivers` tab to check which driver is in use.

**Recommand**: To perform a clean installation, run the following command to remove all residual graphic card drivers and libraries:
```
sudo apt remove --purge nvidia-*
sudo apt remove --purge libnvidia-*
sudo apt remove --purge cuda-*
```

---
### CUDA Toolkits

Go to [Nvidia CUDA Toolkit Downloads](https://developer.nvidia.com/cuda-downloads) page and select the target platform.
| Option           | Description |
| ---------------- | ----------- |
| Operating System | Linux       |
| Architecture     | x86_64      |
| Distribution     | Ubuntu      |
| Version          | 20.04       |
| Installer Type   | deb(local)  |

The command in use for this particular installation are:

```
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/11.7.0/local_installers/cuda-repo-ubuntu2004-11-7-local_11.7.0-515.43.04-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2004-11-7-local_11.7.0-515.43.04-1_amd64.deb
sudo cp /var/cuda-repo-ubuntu2004-11-7-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
sudo apt-get -y install cuda
```
**Caution**:
 1. Do not use the `sudo apt install nvidia-cuda-toolkit` command directly. It will install an older version of CUDA, and we don't want that.
 2. Before installing CUDA, first check the driver version. There is only certain dirver version that can match with a specific CUDA version. For example, CUDA 11.7 requres driver 515.43.04, and CUDA 11.6 requires driver 510.47.03. If those two didn't match, there will be error message pop up during installation. Please check it carefully.

After finishing the installation, reboot the computer. If the toolkit was properly installed, there will be at least one cuda folder in `/usr/local`. In order to let the OS recognize the toolkit we just installed, the environment path should include cuda directory: [^3]
 1. Configure for all users:
    1. Create a start-up script in `/etc/profile.d/`:

        ```
        sudo touch /etc/profile.d/cuda.sh
        ```
    2. Add the following line in that script:

        ```
        #! /usr/bin/sh
        export PATH=/usr/local/cuda-11.7/bin${PATH:+:${PATH}}
        ```
 2. Configure for individual user:
    
    Add the following line at the end of `~/.profile`:
    ```
    export PATH=/usr/local/cuda-11.7/bin${PATH:+:${PATH}}
    ```

Re-login the system, and use the following command to verify the environment path is properly set:

```
gcc --version
nvcc --version
nvidia-smi
```
Using the following command to verify the libraries have been properly loaded by the dynamic linker:

```
ldconfig -p | grep cuda
```
It should be around 60-ish to 70-ish entries on the list.

**Recommended**: To verify the integrity of the installation, run the following cuda example:

```
git clone https://github.com/NVIDIA/cuda-samples.git
cd ./cuda-samples/Samples/1_Utilities/deviceQuery
make
./deviceQuery
```

[^2] [NVIDIA CUDA Installation Guide for Linux](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#abstract)

[^3] [Understand linux shell start up scripts](https://medium.com/coding-blocks/getting-to-understand-linux-shell-s-start-up-scripts-and-the-environments-path-variable-fc672107b2d7)

---
### Install cuDNN Library [^4]
The last thing required for DeepLabCut is the cuDNN library. Goto the [cudnn-download](https://developer.nvidia.com/rdp/cudnn-download) website, login to a nvidia developer account, and download the package corresponds to the architecure(e.g. x86_64) and distribution(e.g. Ubuntu20.04). Open the terminal and navigate to the directory which store the downloaded `.deb` file. Run the following file to add the repository configuration into the system (replace the x in the line into the correct version number):

```
sudo dpkg -i cudnn-local-repo-ubuntu2004-8.x.x.x_x.x-x_amd64.deb
```
Follow the instruction shown at the end of the dpkg output to install the public key:
```
sudo cp /var/cudnn-local-repo-ubuntu2004-8.x.x.x/cudnn-local-xxxxxxxxxx-keyring.gpg /usr/share/keyrings/
```
Refresh the apt package index, and install the library:
```
sudo apt update
sudo apt install libcudnn8-dev
```
Using the following command to verify the libraries have been properly loaded by the dynamic linker:

```
ldconfig -p | grep libcudnn
```
It should be around 10-ish entries on the list.

**Recommended**: To verify the integrity of the installation, run the following cuda example:
```
sudo apt install libcudnn8-samples
sudo apt install libfreeimage3 libfreeimage-dev
cp -r /usr/src/cudnn_samples_v8/ $HOME
cd $HOME/cudnn_samples_v8/mnistCUDNN/
make clean && make
./mnistCUDNN
```
It shouldn't show any error during the compilation. If the last output line from the mnistCUDNN shows `PASS`, means the cuDNN was installed properly.

[^4] [NVIDIA cuDNN Installation Guide](https://docs.nvidia.com/deeplearning/cudnn/install-guide/index.html)

---
## Install Python, and setup the conda environment
### Install Anaconda
Before istalling anaconda GUI package, install the following extended dependencies for Qt by executing:

    sudo apt install libgl1-mesa-glx libegl1-mesa libxrandr2 libxrandr2 libxss1 libxcursor1 libxcomposite1 libasound2 libxi6 libxtst6

Goto  the [Anaconda download](https://www.anaconda.com/products/distribution#Downloads) website to download the installation script. Use the following command to execute the script:
```
bash ~/Downloads/Anaconda3-2022.05-Linux-x86_64.sh
```
Follow the instruction in the terminal to finish the installation.

### Create a conda environment
Create a conda environment for the project:
```
conda create --name vZF python=3.7
```
Note that due to the dependency of DeepLabCut-Live, we currently stick to python 3.7.
### Install DeepLabCut-Live
Install deeplabcut-live:
```
pip install deeplabcut-live
```
**Note**: DeepLabCut-Live requires numpy < 1.19.0, which numpy askes for an older version of tensorflow. If you want DeepLabCut install in the same conda environmet later, install deeplabcut-live prior to avoid potential conflicts.

**Optional**: To verify the integrity of the installation, run the following command to test DeepLabCut-Live:
```
sudo apt install curl
dlc-live-test
```

### Install DeepLabCut
**Caution**: Newest deeplabcut asks for a higher version of numpy, which will further causing conflict with deeplabcut-live. Either stick with a lower version of DeepLabCut, or create a seperate conda environment for DeepLabCut only.

Install deeplabcut and it's dependencies:
```
pip install deeplabcut==2.2.0.6
pip install ffmpeg ipython jupyter torch
```

**Optional**: In order to get the GUI running, we have to build the wxpython. First check all the dependencies of the wxpython are installed.[WxPython dependencies list](https://github.com/wxWidgets/Phoenix/blob/master/README.rst#prerequisites):
```
sudo apt install dpkg-dev build-essential python3-dev freeglut3-dev libgl1-mesa-dev libglu1-mesa-dev libgstreamer-plugins-base1.0-dev libgtk-3-dev libjpeg-dev libnotify-dev libpng-dev libsdl2-dev libsm-dev libtiff-dev libwebkit2gtk-4.0-dev libxtst-dev
```
Next, use the following command to install the wxpython:
```
conda install -c conda-forge gtk3
conda install -c conda-forge wxpython
```
**Optional**: If you wish to automatically activate this conda environment every time login into a terminal, add the following line in your `~/.bashrc` file:
```
conda activate vZF
```


---
## Installation of FLIR Spinnaker SDK
Goto the [Spinnaker SDK Download](https://www.flir.asia/products/spinnaker-sdk/) page, download the installation package matched with our distribution, architecture and python interpreter verion.

**Note**: Due to the dependency of DeepLabCut-Live, python 3.7 was in used. Currently FLIR didn't have a python wrapper supporting python 3.7. Please go to the `Archieve` folder and look for a version that could support python 3.7.

The files in use for this particular installation are:
```
spinnaker-2.5.0.80-Ubuntu20.04-amd64-pkg.tar.gz # Spinnaker SDK
spinnaker_python-2.5.0.80-cp37-cp37m-linux_x86_64.tar.gz # Python wrapper
```

### Install FLIR Spinnaker SDK
Before installing the SDK, install the following extended dependencies:
```
sudo apt-get install libavcodec58 libavformat58 libswscale5 libswresample3 libavutil56 libusb-1.0-0 libpcre2-16-0 libdouble-conversion3 libxcb-xinput0 libxcb-xinerama0
```
Use the following command to un-pack the downloaded file:
```
tar -xvf spinnaker-2.5.0.80-Ubuntu20.04-amd64-pkg.tar.gz
```
Goto the unpacked folder, and execute the installation script:
```
cd ./spinnaker-2.5.0.80-amd64
sudo sh install_spinnaker.sh
```
Follow the instruction in the script to complete the installation.
**Caution**: During the installation process, do add the user to group flirimaging. Otherwise the cameras can only be used by using ROOT accout.

### Install Spinnaker Python wrapper
Use the following command to unpack the downloaded file:
```
mkdir spinnaker_python
mv spinnaker_python-2.5.0.80-cp37-cp37m-linux_x86_64.whl spinnaker_python
cd spinnaker_python
tar -xvf spinnaker_python-2.5.0.80-cp37-cp37m-linux_x86_64.whl
```
Use pip command to install the python wrapper:
```
pip install spinnaker_python-2.5.0.80-cp37-cp37m-linux_x86_64.whl
```

---
## Useful software that is not related to the code

### Vim - Command-line-based text editor

    sudo apt install vim

### Git

    sudo apt install git