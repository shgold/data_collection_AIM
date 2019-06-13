import cv2
import os
import time
import pyzed.sl as sl
import ffmpeg
from shutil import copy2


from utils.print_utils import magenta, yellow
import utils.log_utils as logutils
import utils.zed_utils as zutils


# Set input video and output directory
input_dir = './saved_data/VID/{}/'.format(time.strftime('%Y%m%d'))
output_dir = './saved_data/VID/{}/frames'.format(time.strftime('%Y%m%d'))
log_dir = './saved_data/VID/{}/video_capture.log'.format(time.strftime('%Y%m%d'))


def pairing_videos(pair_list, dest_folder):
    list_num_total = len(pair_list)

    for i, pair in enumerate(pair_list):
        temp_folder = os.path.join(dest_folder, 'set{}'.format(i))
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)
        print('Copying {}th pair out of {} pairs'.format(i, list_num_total))
        copy2(pair[0], temp_folder)
        copy2(pair[1], temp_folder)
        copy2(pair[2], temp_folder)


if __name__ == '__main__':
    date='20190613'

    __INPUT_DIR__ = './saved_data/VID/{}/'.format(date)
    __LOG_FILE__ = './saved_data/VID/{}/video_capture.log'.format(date)
    __OUTPUT_DIR__ = './saved_data/VID/{}/sorted'.format(date)


    # list is in [D5, P20, ZED] order
    list_vid_dir = logutils.read_log_file(__LOG_FILE__, __INPUT_DIR__, is_video=True)

    pairing_videos(list_vid_dir, __OUTPUT_DIR__)


    print('Done!')