# data_collection_AIM
This repository contains the scripts for collecting images and videos from three different cameras.

## Objective
The objective of collecting this dataset is to be used in the future image/video enhancement research, for example, image super resolution, video super resolution and etc. We are using three different cameras, Huawei P20, Canon EOS D5 Mark IV and ZED stereo camera, which represent smartphone camera, high-end DSLR camera and depth sensing camera respectively. 

## Data collection setup
We collect sets of images or videos from three different cameras such as Huawei P20, Canon EOS D5 Mark IV and ZED stereo camera. These cameras are fixed in a special rig (TODO: setup image), and all of the cameras are connected to the laptop through USB 3.0 port. The bluetooth mouse connected to the laptop will be a controller to command the shootings of all cameras.

(TODO: Indicate how each camera is set (p20 developer mode, auto) (D5 auto) (ZED Ultra depth))

By executing `exe_IMG_trigger_all.py` or `exe_VID_trigger_all.py`, all the devices will be triggered within the time differences of less than a second.

## Requirements of computer(laptop)
- Ubuntu 18.04 LTS
- NVIDIA GPU with CUDA version 10.0 installed (necessary requirement to use ZED stereo camera)
- NVIDIA driver version 410.104

## Pre-installed libraries
Some libraries should be installed to control cameras remotely from the scripts.

We are using [gphoto2](http://www.gphoto.org/) to control Canon D5 Mark IV remotely.
```
$ sudo apt-get install gphoto2
```
We are using [adb](https://developer.android.com/studio/command-line/adb) to control Huawei P20 in the developer mode.
```
$ sudo apt-get install adb
```
We are using [ZED SDK 2.8](https://www.stereolabs.com/developers/release/#sdkdownloads_anchor) and [ZED python-API](https://github.com/stereolabs/zed-python-api) to run ZED stereo camera. 
```
Please follow the official instruction to install ZED software. 
```
The other libraries installed.
- pynput(version 1.4.2) ` $ pip3 install pynput`
- opencv(version 4.1.0) ` $ pip3 install opencv-python`
- ffmpeg(version 3.4.6) ` $ sudo apt-get install ffmpeg`  and ` $ pip3 install ffmpeg-python`

## Usage of the scripts
### 1. Capture images

In order to capture images, first set up the devices properly and make sure that they are on the right mode for capturing. (For example, we set Huawei P20 camera app in an PRO mode and Canon D5 Mark IV in an AUTO mode.)

  Then you can run, 
  ```
  $ python3 exe_IMG_trigger_all.py --p20 --zed --d5 --zed_rest 5
  ```
  When the script is running, click mouse LEFT button to trigger the cameras. Once the capturing is finished the alarm will go off and it is ready to take next images. 
  - `p20`, `zed`, `d5` are the flags indicating the devices that you will use to collect data. 
  - `zed_rest` is a period of time(in seconds) which allows ZED camera to adjust to the light of the environment when opened. The default value is 5 seconds. 

  When capturing is finished, click mouse RIGHT button and wait until another alarms(4 times) go off. 
  
### 2. Record videos

  In order to capture videos, first set up the devices properly and make sure that they are on the right mode for recording. (For example, we set Huawei P20 camera app in an VIDEO mode and Canon D5 Mark IV in an AUTO video recording mode.)

  Then you can run,
  ```
  $ python3 exe_VID_trigger_all.py --p20 --zed --d5 --vid_time 20 --zed_rest 5
  ```
  When the script is running, click mouse LEFT button to trigger the cameras. Once the recording is finished the alarm will go off and it is ready to take next videos. 
  - `p20`, `zed`, `d5` are the flags indicating the devices that you will use to collect data.
  - `vid_time` is a period of time(in seconds) that you will going to record. The default of recording period is 20 seconds. 
  - `zed_rest` is a period of time(in seconds) which allows ZED camera to adjust to the light of the environment when opened. The default value is 5 seconds. 
  When capturing is finished, click mouse RIGHT button and wait until another alarms(4 times) go off. 

### 3. Saved data structure
All the recorded data will be saved in the `saved_data` folder in the same directory of this repository. 
The structure of the data will be like following. 


    saved_data
    |
    ├── IMG 
    │   ├── 20190610                               # Date of data collection
    |   │   ├── D5                                 # Images captured from Canon D5 Mark IV 
    |   |   |   ├── CD5_0123.CR2                   # Raw image
    |   |   |   ├── CD5_0123.JPG                   # JPEG image
    |   |   |   └── ...
    │   |   ├── P20                                # Images captured from Huawei P20
    |   |   |   ├── RAW                            # Raw image folder
    |   |   |   |   ├── IMG_20190610_122402.dng
    |   |   |   |   └── ...
    |   |   |   ├── IMG_20190610_122402.jpg        # JPEG image
    |   |   |   └── ...
    |   |   ├── ZED                                # Images captured from ZED stereo camera
    |   |   |   ├── 1560170958                     # ZED images folder
    |   |   |   |   ├── ZED_IMG_raw.svo            # RAW data from the ZED camera
    |   |   |   |   ├── zed_camera_param.txt       # Parameters of the ZED camera when taking the image
    |   |   |   |   └── ...
    |   |   |   └── ...
    |   |   └── image_capture.log                  # Log file of the captured data in one day
    │   ├── 20190611         
    │   └── ...          
    |
    ├── VID                    
    │   ├── 20190610                               # Date of data collection
    |   │   ├── D5                                 # Videos captured from Canon D5 Mark IV 
    |   |   |   ├── CD5_0123.MOV                   # MPEG video
    |   |   |   └── ...
    │   |   ├── P20                                # Videos captured from Huawei P20
    |   |   |   ├── VID_20190610_122402.mp4       # MPEG video
    |   |   |   └── ...
    |   |   ├── ZED                                # Videos captured from ZED stereo camera
    |   |   |   ├── ZED_VID_20190610122402.svo     # RAW data from the ZED camera
    |   |   |   └── ...
    |   |   └── video_capture.log                  # Log file of the captured data in one day
    │   ├── 20190611          
    │   └── ...              
    └── ...


## Other useful functions
### 1. sorting the data in one folder
After collecting data, using `help_sort_data_by_logs.py` script will help you pairing the data in seperate folders. For example, [saved_data/20190611/sorted/set_ori1], [saved_data/20190611/sorted/set_ori2], and so on. 
  ```
  $ python3 help_sort_data_by_logs.py --date 20190623 --mode IMG --set_continue 0 --convertSVO
  ```
  - `date` is the date of data collection. The corresponding date folder should be under `saved_data`.
  - `mode` is the type of data that you want to sort. Either IMG or VID.
  - `set_continue` is the starting number of the newly paired folders. The default is 0.
  - `converSVO` is the flag which converts ZED's .svo file into .png(if mode is IMG) or .avi(if mode is VID).
  
### 2. Checking images easily
Explain here

### 3. Converting Videos to Frames
You can use `/useful_functions/temp_vids_to_frames.py` script to conver videos into frames(in .png format). It requires opencv2 library and ZED python API to run this script successfully. 
- You have to define `__INPUT_DIR__` as a top folder which stores the `set_ori[NR]`. 
- It will create `zed_frames` and `canon_frames` under the same `set_ori[NR]` folders. 
```
$ python3 temp_vids_to_frames.py 
```

  

## Common troubleshootings
#### 1. Check all devices are ON and in the right mode
When the device is not turned on nor on the right mode(for example, running video recording scripts when cameras are on the photo taking mode or vice versa), the capturing process won't work properly. 
#### 2. ERROR 70 happening in Canon D5 Mark IV
Sometimes canon camera fires error message on its LCD screens when during capturing. This happens when camera went to sleeping mode while waiting for the next shootings. In this case, please turn off the camera and unplug the USB cable from the computer. Then re-connect the camera again back to the computer.



## Contributing
Feel free to open an issue if you find a bug, or a pull request for bug fixes, features or other improvements.
