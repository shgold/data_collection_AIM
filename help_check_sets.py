import cv2
import os
import time
import pyzed.sl as sl
import ffmpeg
from shutil import copy2, copytree, move
import argparse
import numpy as np

from utils.print_utils import magenta, yellow, red

class sorted_set_loader(object):
    def __init__(self, input_dir, output_dir_clean, output_dir_hold, output_dir_discard):
        self.input_dir = input_dir
        self.output_dir_clean = output_dir_clean
        self.output_dir_hold = output_dir_hold
        self.output_dir_discard = output_dir_discard


        # Create the output directories if not exists
        if not os.path.exists(self.output_dir_clean):
            os.makedirs(self.output_dir_clean)

        if not os.path.exists(self.output_dir_hold):
            os.makedirs(self.output_dir_hold)

        if not os.path.exists(self.output_dir_discard):
            os.makedirs(self.output_dir_discard)

        # Create set list from the input directory
        self.set_list = os.listdir(input_dir)

        self.current_set = None
        self.prev_set = None
        self.next_set = None

    def check_images(self):
        self.print_helpping_messages()
        # Check if there is folder need to be inspectedssss
        if len(self.set_list) == 0:
            print(red('No sets to inspect - please check the folder'))
            return -1

        set_pointer = self.set_list[-1]

        while True:
            print(len(self.set_list))
            # Check if there is folder need to be inspectedssss
            if len(self.set_list) == 0:
                print(red('No more sets to inspect '))
                break

            new_key = self.check_current_folder(set_pointer)

            current_set_index = self.set_list.index(self.current_set)
            if chr(new_key) == 'n':
                if current_set_index < len(self.set_list)-1:
                    set_pointer = self.set_list[current_set_index +1]
                else:
                    print(red('This set is the end of the list'))

            elif chr(new_key) == 'p':
                if current_set_index > 0:
                    set_pointer = self.set_list[current_set_index - 1]
                else:
                    print(red('This set is the first of the list'))

            elif chr(new_key) in ['s', 'h', 'd']:
                set_pointer = self.move_items_accordingly(new_key)

            elif chr(new_key) == 'q':
                print('Exiting the program')
                break

            else:
                print(red('[!]Please press the right key'))
                self.print_helpping_messages()

    def move_items_accordingly(self, key):
        source = os.path.join(self.input_dir, self.current_set)
        if chr(key) == 's':
            move(source, self.output_dir_clean)
            print('Moving {} to {}'.format(self.current_set, self.output_dir_clean))

        if chr(key) == 'd':
            move(source, self.output_dir_discard)
            print('Moving {} to {}'.format(self.current_set, self.output_dir_discard))

        if chr(key) == 'h':
            move(source, self.output_dir_hold)
            print('Moving {} to {}'.format(self.current_set, self.output_dir_hold))

        # Remove the current folder from the list and reset the pointer
        self.set_list.pop()
        if len(self.set_list) > 0:
            set_pointer = self.set_list[-1]
        else:
            set_pointer = None
        return set_pointer


    def print_helpping_messages(self):
        print(yellow('n: go to next folder \ p: go to previous folder'))
        print(yellow('s: move items into a saving folder'))
        print(yellow('h: move items into a hold folder'))
        print(yellow('d: move items into a deleting folder'))

    def check_current_folder(self, current_set):

        self.current_set = current_set
        print('==> Checking {}'.format(current_set))
        print(magenta('1: D5 / 2: P20 / 3: ZED_rgb / 4: ZED_depth / 5:ZED_confidence'))

        self.get_images_in_current_set(current_set)
        self.show_images('1')
        while True:
            key = cv2.waitKey()
            cv2.destroyAllWindows()
            self.show_images(chr(key))
            if chr(key) not in ['1', '2', '3', '4', '5']:
                print('Pressed key is ', chr(key))
                break

        return key


    def get_images_in_current_set(self, current_set):
        images_list = os.listdir(os.path.join(self.input_dir, current_set))
        d5 = [x for x in images_list if '.JPG' in x]
        p20 = [x for x in images_list if '.jpg' in x]
        zed_rgb_left = [x for x in images_list if ('left' in x) and ('unrectified' not in x) and ('depth' not in x)]
        zed_rgb_right = [x for x in images_list if ('right' in x) and ('unrectified' not in x) and ('depth' not in x)]
        zed_depth_left = [x for x in images_list if 'depth_left' in x]
        zed_depth_right = [x for x in images_list if 'depth_right' in x]
        zed_confidence = [x for x in images_list if 'confidence' in x]

        self.d5_img = cv2.imread(os.path.join(self.input_dir, current_set, d5[0]))
        self.p20_img = cv2.imread(os.path.join(self.input_dir, current_set, p20[0]))

        zed_rgb_left = cv2.imread(os.path.join(self.input_dir, current_set, zed_rgb_left[0]))
        zed_rgb_right = cv2.imread(os.path.join(self.input_dir, current_set, zed_rgb_right[0]))
        self.zed_rgb = np.hstack([zed_rgb_left, zed_rgb_right])

        zed_depth_left = cv2.imread(os.path.join(self.input_dir, current_set, zed_depth_left[0]))
        zed_depth_right = cv2.imread(os.path.join(self.input_dir, current_set, zed_depth_right[0]))
        self.zed_depth = np.hstack([zed_depth_left, zed_depth_right])

        self.zed_confidence_img = cv2.imread(os.path.join(self.input_dir, current_set, zed_confidence[0]))

    def show_images(self, key):
        if key == '1':
            cv2.namedWindow('D5_image', cv2.WINDOW_KEEPRATIO)
            cv2.resizeWindow('D5_image', 1600, 1200)

            cv2.imshow('D5_image', self.d5_img)

        if key == '2':
            cv2.namedWindow('P20_image', cv2.WINDOW_KEEPRATIO)
            cv2.resizeWindow('P20_image', 1600, 1200)
            cv2.imshow('P20_image', self.p20_img)

        if key == '3':
            cv2.namedWindow('ZED_image', cv2.WINDOW_KEEPRATIO)
            cv2.resizeWindow('ZED_image', 1600, 1200)
            cv2.imshow('ZED_image', self.zed_rgb)

        if key == '4':
            cv2.namedWindow('ZED_depth', cv2.WINDOW_KEEPRATIO)
            cv2.resizeWindow('ZED_depth', 1600, 1200)
            cv2.imshow('ZED_depth', self.zed_depth)

        if key == '5':
            cv2.namedWindow('ZED_confidence', cv2.WINDOW_KEEPRATIO)
            cv2.resizeWindow('ZED_confidence', 1600, 1200)
            cv2.imshow('ZED_confidence', self.zed_confidence_img)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, help="A date(in YYmmDD format) which you want to process.(example: 20190612)")
    parser.add_argument("--mode", type=str, help="Which dataset that you want to sort out. [IMG | VID]")
    parser.add_argument('--set_continue', default= 0, type=int, help='Continue to create the set from this number.')
    #parser.add_argument('--convertSVO', action='store_true')
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


        # # list is in [D5, P20, ZED] order
        # list_vid_dir = logutils.read_log_file(__LOG_FILE__, __INPUT_DIR__, is_video=True)
        #
        # put_videos_pairs_in_folder(list_vid_dir, __OUTPUT_DIR__, set_count)
        #
        # if args.convertSVO:
        #     make_svo2avi(__OUTPUT_DIR__)

    else: # images
        __INPUT_DIR__ = './saved_data/IMG/{}/sorted'.format(date)
        #__LOG_FILE__ = './saved_data/IMG/{}/image_capture.log'.format(date)
        __OUTPUT_DIR_CLEAN__ = './saved_data/IMG/{}/sorted_clean'.format(date)
        __OUTPUT_DIR_HOLD__ = './saved_data/IMG/{}/sorted_hold'.format(date)
        __OUTPUT_DIR_DISCARD__ = './saved_data/IMG/{}/sorted_discard'.format(date)

        set_list = os.listdir(__INPUT_DIR__)

        helper = sorted_set_loader(__INPUT_DIR__, __OUTPUT_DIR_CLEAN__, __OUTPUT_DIR_HOLD__, __OUTPUT_DIR_DISCARD__)
        helper.check_images()

    print('Done!')