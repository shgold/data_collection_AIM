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
  $ python3 exe_IMG_trigger_all.py --p20 --zed --d5
  ```
  When the script is running, click mouse LEFT button to trigger the cameras. Once the capturing is finished the alarm will go off and it is ready to take next images.

  When capturing is finished, click mouse RIGHT button and wait until another alarms go off. 
  > Make sure you use mouse buttons to turn off the program so that files can be downloaded properly from Huawei P20.

### 2. Record videos

  In order to capture videos, first set up the devices properly and make sure that they are on the right mode for recording. (For example, we set Huawei P20 camera app in an VIDEO mode and Canon D5 Mark IV in an AUTO video recording mode.)

  Then you can run,
  ```
  $ python3 exe_VID_trigger_all.py --p20 --zed --d5 --vid_time 20
  ```
  When the script is running, click mouse LEFT button to trigger the cameras. Once the recording is finished the alarm will go off and it is ready to take next videos. The default of recording period is set to 20 seconds.
  
  When capturing is finished, click mouse RIGHT button and wait until another alarms go off. 
  > Make sure you use mouse buttons to turn off the program so that files can be downloaded properly from Huawei P20.

## Common troubleshootings
#### 1. Check all devices are ON and in the right mode
When the device is not turned on nor on the right mode(for example, running video recording scripts when cameras are on the photo taking mode or vice versa), the capturing process won't work properly. 
#### 2. ERROR 70 happening in Canon D5 Mark IV
Sometimes canon camera fires error message on its LCD screens when during capturing. This happens when camera went to sleeping mode while waiting for the next shootings. In this case, please turn off the camera and unplug the USB cable from the computer. Then re-connect the camera again back to the computer.



## Contributing
Feel free to open an issue if you find a bug, or a pull request for bug fixes, features or other improvements.
