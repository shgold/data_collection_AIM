from pynput.mouse import Listener
import os
import time
from multiprocessing import Pool, Process, cpu_count

from utils.print_utils import yellow, cyan
import utils.canon_utils as canon
import utils.adb_utils as adb
import utils.log_utils as logutils

__D5_VID_PATH__ = './saved_data/VID/{}/D5'.format(time.strftime('%Y%m%d'))
__ZED_VID_PATH__ = "./saved_data/VID/{}/ZED".format(time.strftime('%Y%m%d'))
__P20_VID_PATH__ = "./saved_data/VID/{}/P20".format(time.strftime('%Y%m%d'))

__VID_LOGGING_FILE__ = "./saved_data/VID/{}/video_capture.log".format(time.strftime('%Y%m%d'))
__VID_TIME__ = 10

def beep(count):
    for i in range(count):
        os.system('\a')
        time.sleep(0.2)

def make_dir_if_not_exists(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def capture_P20_video():
    '''
        Capturing the videos using android phone.
        We assume that the camera is ON and on the Video-mode
    :return:
    '''
    starting_time = time.time()
    print('{} starting P20'.format(starting_time))

    #adb.camera_focus()
    adb.press_shutter_button()
    #print('Start taking videos for {} seconds'.format(__VID_TIME__))
    time.sleep(__VID_TIME__)
    adb.press_shutter_button()

    devtime = adb.get_device_time()
    vid_name = adb.get_vid_name()
    vid_logger.info('VIDEO:P20:{}:{}'.format(devtime, vid_name+'.mp4'))

    time_period = time.time() - starting_time
    print('[{:.3f}s] exiting P20'.format(time_period))


def capture_D5_video():
    '''
            Capturing the video using DSLR camera.
            Make sure that the camera is ON and on the right mode for capturing
    :return:
    '''
    starting_time = time.time()
    print('{} starting D5'.format(starting_time))

    d5_stdout = canon.take_video_and_download(directory =__D5_VID_PATH__, time = __VID_TIME__)
    d5_stdout = d5_stdout.split('Saving file as')[-1]
    d5_stdout = d5_stdout.split('\n')[0]
    d5_vid_name = d5_stdout.split('/')[-1]

    time_period = time.time() - starting_time
    print('[{:.3f}s] exiting D5'.format(time_period))
    vid_logger.info('VIDEO:D5:{}'.format(d5_vid_name))


def run_process4video(process):
    '''
        Run the multiprocessing of running all cameras when mouse-click is triggered.
    :param process: A list of process(in str format) to run in parallel.
    :return:
    '''

    #os.system('python3 {}'.format(process))
    if process == 'zed':
        os.system('python3 run_ZED.py --out_path {} --log_file {} --vid_time {}'.format(__ZED_VID_PATH__, __VID_LOGGING_FILE__, __VID_TIME__))

    elif process == 'p20':
        time.sleep(0.5)
        capture_P20_video()

    elif process == 'D5':
        time.sleep(1)
        capture_D5_video()
    else:
        print('nothing to run')
        pass


def on_click_run(x, y, button, pressed):
    if pressed:
        print('{0} {1} at {2}'.format('Pressed' if pressed else 'Released', button, (x, y)))

        if button.name == 'left': # when clicking left button, run the processes
            vid_logger.info('=====START=====')
            print('In video recording mode: ')

            processes = ['zed', 'D5', 'p20']
            pool = Pool(processes=len(processes))
            pool.map(run_process4video, processes)

            # Alarm that all the processes are finished,
            # and ready for the next process.
            beep(1)

        else: # when clicking right button, exit the process
            return False



if __name__ == '__main__':

    print('Starting')
    make_dir_if_not_exists(__ZED_VID_PATH__)
    make_dir_if_not_exists(__P20_VID_PATH__)
    make_dir_if_not_exists(__D5_VID_PATH__)

    # Create logger
    vid_logger = logutils.create_logger(__VID_LOGGING_FILE__)

    # Clean P20 camera folder
    adb.clean_camera_folder()

    # Kill the process which blocks the camera connection
    canon.killGphoto2Process()

    print(yellow('Make sure that all the devices are on and at the right mode!'))
    print(cyan('============== Guide ================'))
    print(cyan('Mouse LEFT click to record videos.'))
    print(cyan('Mouse RIGHT click to exit the program.'))

    # Collect events until released
    with Listener(on_click=on_click_run) as listener:
        listener.join()

    # Download files captured from P20
    adb.transfer_media_files(__P20_VID_PATH__)

    # Alarm that this program is closed.
    beep(3)
    print('Done!')