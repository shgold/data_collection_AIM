import cv2
import os
import time
import pyzed.sl as sl
import ffmpeg
from shutil import copy2
import argparse


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


def make_svo2avi(sorted_folder_dir):
    '''
        Convert ZED .svo file into .avi file. in the same folder
    :param sorted_folder_dir: A folder directory(ex. /sorted) where zed file is stored.
    :return:
    '''
    for folder in os.listdir(sorted_folder_dir):
        __SUB_DIR__ = os.path.join(sorted_folder_dir, folder)
        files = os.listdir(__SUB_DIR__)

        zed_vid_name = None
        for f in files:
            if '.svo' in f:
                zed_vid_name = f.split('.svo')[0]

        if zed_vid_name is not None:
            svo_file = os.path.join(__SUB_DIR__, zed_vid_name + '.svo')
            avi_file = os.path.join(__SUB_DIR__, zed_vid_name + '.avi')
            os.system('python3 ZED_SVO_Export.py {} {} 1'.format(svo_file, avi_file))

        print('Done!')



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, help="A date(in YYmmDD format) which you want to process.(example: 20190612)")
    args = parser.parse_args()

    date= args.date

    __INPUT_DIR__ = './saved_data/VID/{}/'.format(date)
    __LOG_FILE__ = './saved_data/VID/{}/video_capture.log'.format(date)
    __OUTPUT_DIR__ = './saved_data/VID/{}/sorted'.format(date)


    # list is in [D5, P20, ZED] order
    list_vid_dir = logutils.read_log_file(__LOG_FILE__, __INPUT_DIR__, is_video=True)

    pairing_videos(list_vid_dir, __OUTPUT_DIR__)

    make_svo2avi(__OUTPUT_DIR__)




    print('Done!')

