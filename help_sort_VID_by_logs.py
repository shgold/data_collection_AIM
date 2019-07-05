import cv2
import os
import time
import pyzed.sl as sl
import ffmpeg
from shutil import copy2, copytree
import argparse


from utils.print_utils import magenta, yellow, red
import utils.log_utils as logutils
import utils.zed_utils as zutils


# Set input video and output directory
input_dir = './saved_data/VID/{}/'.format(time.strftime('%Y%m%d'))
output_dir = './saved_data/VID/{}/frames'.format(time.strftime('%Y%m%d'))
log_dir = './saved_data/VID/{}/video_capture.log'.format(time.strftime('%Y%m%d'))

def copy_folders(src_dir, dest_dir):
    dir_basename = os.path.basename(src_dir)

    dest_dir = os.path.join(dest_dir, dir_basename)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for files in os.listdir(src_dir):
        file_dir = os.path.join(src_dir, files)
        copy2(file_dir, dest_dir)



def put_videos_pairs_in_folder(pair_list, dest_folder, set_count):
    list_num_total = len(pair_list)

    for i, pair in enumerate(pair_list):
        temp_folder = os.path.join(dest_folder, 'set{}/'.format(i+set_count))
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)
        print('Copying {}th pair out of {} pairs'.format(i, list_num_total))
        copy2(pair[0], temp_folder) # D5
        copy2(pair[1], temp_folder) # P20
        copy2(pair[2], temp_folder) # ZED

    print(magenta('Finishing copying videos in pairs'))


def put_images_pairs_in_folder(pair_list, dest_folder, set_count):
    list_num_total = len(pair_list)

    for i, pair in enumerate(pair_list):
        temp_folder = os.path.join(dest_folder, 'set{}'.format(i+set_count))
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)
        print('Copying {}th pair out of {} pairs'.format(i, list_num_total))

        try:
            copy2(pair[0][0], temp_folder)    # D5 jpg
            copy2(pair[0][1], temp_folder)    # D5 cv2
            copy2(pair[1][0], temp_folder) # p20 jpg
            copy2(pair[1][1], temp_folder) # p20 dng
            copy_folders(pair[2], temp_folder)    # zed folders
        except:
            print(yellow('File does not exists '))
            pass

    print(magenta('Finishing copying images in pairs'))


def make_svo2avi(out_folder_dir):
    '''
        Convert ZED .svo file into .avi file. in the same folder
    :param sorted_folder_dir: A folder directory(ex. /sorted) where zed file is stored.
    :return:
    '''
    for folder in os.listdir(out_folder_dir):

        __SUB_DIR__ = os.path.join(out_folder_dir, folder)
        files = os.listdir(__SUB_DIR__)

        zed_vid_name = None
        for f in files:
            if '.svo' in f:
                zed_vid_name = f.split('.svo')[0]

        if zed_vid_name is not None:
            svo_file = os.path.join(__SUB_DIR__, zed_vid_name + '.svo')
            avi_file = os.path.join(__SUB_DIR__, zed_vid_name + '.avi')
            os.system('python3 ZED_SVO_Export.py {} {} 1'.format(svo_file, avi_file))

    print(magenta('Finishing converting svo videos to avi'))


def make_svo2png(out_folder_dir):
    '''
        Convert ZED .svo file into .png file(rgb, depth images) in the same folder
    :param out_folder_dir: A folder directory(ex. /sorted) where zed file is stored.
    :return:
    '''
    for folder in os.listdir(out_folder_dir):
        __SUB_DIR__ = os.path.join(out_folder_dir, folder)
        files = os.listdir(__SUB_DIR__)

        zed_img_name = None
        for f in files:
            if '.svo' in f:
                zed_img_name = f.split('.svo')[0]

        depth_file = os.path.join(__SUB_DIR__, 'zed_depth_left.png')
        if os.path.exists(depth_file):
            continue

        if zed_img_name is not None:
            svo_file = os.path.join(__SUB_DIR__, zed_img_name + '.svo')
            txt_file = os.path.join(__SUB_DIR__, 'zed_camera_param.txt')
            out_file = os.path.join(__SUB_DIR__, 'zed')

            zed, runtime = zutils.configure_zed_camera(svo_file=svo_file)

            zed.set_depth_max_range_value(40000)  # Set the maximum depth perception distance to 40m

            # Get parameters of the image
            gain, brightness, contrast, exposure, hue, saturation, whitebalance = zutils.get_params_from_txt_file(txt_file)
            zed.set_camera_settings(sl.CAMERA_SETTINGS.CAMERA_SETTINGS_GAIN, gain, False)
            zed.set_camera_settings(sl.CAMERA_SETTINGS.CAMERA_SETTINGS_BRIGHTNESS, brightness, False)
            zed.set_camera_settings(sl.CAMERA_SETTINGS.CAMERA_SETTINGS_CONTRAST, contrast, False)
            zed.set_camera_settings(sl.CAMERA_SETTINGS.CAMERA_SETTINGS_EXPOSURE, exposure, False)
            zed.set_camera_settings(sl.CAMERA_SETTINGS.CAMERA_SETTINGS_HUE, hue, False)
            zed.set_camera_settings(sl.CAMERA_SETTINGS.CAMERA_SETTINGS_SATURATION, saturation, False)
            zed.set_camera_settings(sl.CAMERA_SETTINGS.CAMERA_SETTINGS_WHITEBALANCE, whitebalance, False)

            if zed.grab(runtime) == sl.ERROR_CODE.SUCCESS:
                zutils.save_rgb_image(zed, out_file)
                zutils.save_unrectified_rgb_image(zed, out_file)
                zutils.save_depth(zed, out_file)
                zutils.save_other_image(zed, out_file)
                zutils.save_parameters(zed, out_file)

            zed.close()

    print(magenta('Finishing converting svo images to png'))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, help="A date(in YYmmDD format) which you want to process.(example: 20190612)")
    parser.add_argument("--mode", type=str, help="Which dataset that you want to sort out. [IMG | VID]")
    parser.add_argument('--set_continue', default= 0, type=int, help='Continue to create the set from this number.')
    parser.add_argument('--convertSVO', action='store_true')
    args = parser.parse_args()

    date= args.date
    mode = args.mode
    set_count = args.set_continue

    if mode != 'IMG' and mode !='VID':
        print(red('Please choose the mode between [ IMG | VID ]'))
        exit(-1)

    if mode == 'VID':
        __INPUT_DIR__ = './saved_data/VID/{}/'.format(date)
        __LOG_FILE__ = './saved_data/VID/{}/video_capture.log'.format(date)
        __OUTPUT_DIR__ = './saved_data/VID/{}/sorted'.format(date)


        # list is in [D5, P20, ZED] order
        list_vid_dir = logutils.read_log_file(__LOG_FILE__, __INPUT_DIR__, is_video=True)

        put_videos_pairs_in_folder(list_vid_dir, __OUTPUT_DIR__, set_count)

        if args.convertSVO:
            make_svo2avi(__OUTPUT_DIR__)

    else: # images
        __INPUT_DIR__ = './saved_data/IMG/{}/'.format(date)
        __LOG_FILE__ = './saved_data/IMG/{}/image_capture.log'.format(date)
        __OUTPUT_DIR__ = './saved_data/IMG/{}/sorted'.format(date)

        # list is in [D5, P20, ZED] order
        list_vid_dir = logutils.read_log_file(__LOG_FILE__, __INPUT_DIR__, is_video=False)

        put_images_pairs_in_folder(list_vid_dir, __OUTPUT_DIR__, set_count)

        if args.convertSVO:
            make_svo2png(__OUTPUT_DIR__)

    print('Done!')

