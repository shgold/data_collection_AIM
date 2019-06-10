import os
from subprocess import check_output, call
from time import clock, sleep

__CAMERA_PATH__ = '/storage/emulated/0/DCIM/Camera/'
__SENSOR_LOG_PATH__ = '/storage/sdcard0/MySensorStreams/'
DEBUG = False

def open_camera():
    # # check if camera is the top most: adb shell dumpsys activity activities | grep mFocusedActivity --> mFocusedActivity: ActivityRecord{f9da72a u0 com.sec.android.app.camera/.Camera t3967}
    if DEBUG: print('open_camera'.ljust(20), clock())
    r = check_output(['adb', 'shell', 'am', 'start', '-a', 'android.media.action.STILL_IMAGE_CAMERA'])
    if DEBUG: print (r.strip())


def check_file_name_in_folder(folder, file_type=None):
    if DEBUG: print('checking camera folder')

    file_list = check_output(['adb', 'shell', 'ls', folder])
    file_list = file_list.decode('utf-8')

    file_name = []
    if file_type is not None:
        for f in file_list.split():
            if f.find(str(file_type)) > 0:
                file_name.append(f.split('.')[0])

    if len(file_name) == 0:
        file_name = None

    return file_name


def check_if_file_exist(folder):
    if DEBUG: print('checking folder {}'.format(folder))
    file_list = check_output(['adb', 'shell', 'ls', folder])
    file_list = file_list.decode('utf-8')
    count_files = file_list.count('\n')

    if count_files == 0:
        out = None
    else:
        if file_list.find('cache')==0:
            out = None
        else:
            out = True

    if out is None:
        print('No files found in the folder {}'.format(folder))
    else:
        print('{} files found in the folder {}'.format(count_files, folder))
    return out


def clean_camera_folder():
    # delete from phone: adb shell rm /sdcard/DCIM/Camera/*
    if DEBUG: print('clear_camera_folder'.ljust(20), clock())

    img_files=check_file_name_in_folder(folder = __CAMERA_PATH__, file_type='jpg')
    vid_files=check_file_name_in_folder(folder = __CAMERA_PATH__, file_type='mp4')

    if DEBUG: print(img_files, vid_files)

    if (img_files is None) & (vid_files is None):
        log = 'No image/video files to delete'
    else:
        r = check_output(['adb', 'shell', 'rm', '-r', os.path.join(__CAMERA_PATH__, '*')])
        log = 'Camera folder is cleaned'

    print(log)

def clean_folder(folder):
    # delete from phone: adb shell rm  folder_path
    if DEBUG: print('clean_folder'.format(folder), clock())

    file = check_if_file_exist(__SENSOR_LOG_PATH__)
    if file is not None:
        r = check_output(['adb', 'shell', 'rm', '-r', os.path.join(folder, '*')])
        log = 'All the files in the {} is removed from phone'.format(folder)

    print(log)



def toggle_camera_mode(direction):
    assert(direction == 'r' )|(direction == 'l'), 'direction should be given either r(right) of l(left)'

    if direction =='r':
        if DEBUG: print('mode changed to the right')
        call(['adb', 'shell', 'input', 'tap', '700', '1700'])
    else:
        if DEBUG: print('mode changed to the left')
        call(['adb', 'shell', 'input', 'tap', '400', '1700'])


def camera_focus():
    # condition 1 screen on 2 camera open: adb shell input keyevent = CAMERA
    if DEBUG: print('focusing the camera'.ljust(20), clock())
    call(['adb', 'shell', 'input', 'keyevent', 'KEYCODE_FOCUS'])


def press_shutter_button():
    # condition 1 screen on 2 camera open: adb shell input keyevent = CAMERA
    if DEBUG: print('[p20] press_camera_button'.ljust(20), clock())
    call(['adb', 'shell', 'input', 'keyevent', 'KEYCODE_CAMERA'])


def transfer_media_files(path):
    # looking for last file in DCIM/Camera: NO NEED cause we just have 1 picture (clear folder before capture)
    # copy to PC: adb pull /sdcard/DCIM/Camera/ c:/temp
    if DEBUG: print('screen transfer_img'.ljust(20), clock())
    while 1:
        file = check_if_file_exist(__CAMERA_PATH__)
        if file is not None:
            r = check_output(['adb', 'pull', __CAMERA_PATH__, path])
            if DEBUG: print(r.strip())
            break

def get_img_name():
    r = check_output(['adb', 'shell', 'date', '+IMG_%Y%m%d_%H%M%S'])
    img_name = r.decode('utf-8')[:-1]
    return img_name

def get_vid_name():
    r = check_output(['adb', 'shell', 'date', '+VID_%Y%m%d_%H%M%S'])
    img_name = r.decode('utf-8')[:-1]
    return img_name

def get_device_time():
    r = check_output(['adb', 'shell', 'cat', '/proc/uptime'])
    if DEBUG:
        print(r.strip())
    device_time = str.split(r.decode('utf-8'))[0]
    return device_time

def transfer_log_files(path):
    # looking for log files in the sdcard
    if DEBUG: print('download the log files'.ljust(20), clock())
    file = check_if_file_exist(__SENSOR_LOG_PATH__)
    if file is not None:
        r = check_output(['adb', 'pull', '-a',  __SENSOR_LOG_PATH__, path])
        if DEBUG: print(r.strip())


def screen_off():
    # assume it already on: adb shell input keyevent = POWER
    if DEBUG: print('screen_off'.ljust(20), clock())
    r = check_output(['adb', 'shell', 'input', 'keyevent', 'KEYCODE_HOME'])
    r = check_output(['adb', 'shell', 'input', 'keyevent', 'KEYCODE_POWER'])
    if DEBUG: print(r.strip())

def screen_on():
    # assume it already on: adb shell input keyevent = POWER
    if DEBUG: print('screen_on'.ljust(20), clock())
    r = check_output(['adb', 'shell', 'input', 'keyevent = POWER'])
    r = check_output(['adb', 'shell', 'input', 'swipe', '100', '1300', '800', '1300'])
    if DEBUG: print(r.strip())


