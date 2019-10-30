import os
from shutil import copy2, copytree, move
import numpy as np
import cv2
import time

import pyzed.sl as sl
import argparse

__PATH__ = '/media/dc2019/My Book/IMG/'
__DEST_PATH__ = '/media/dc2019/My Book/SORTED/'

def save_rgb_zed_image(zed, dest_dir, numset):
    image_sl_left = sl.Mat()
    image_sl_right = sl.Mat()

    try:
        zed.retrieve_image(image_sl_left, sl.VIEW.VIEW_LEFT)
        zed.retrieve_image(image_sl_right, sl.VIEW.VIEW_RIGHT)
    except:
        print("Failed... Please check that you have permissions to write on disk")
        return -1

    image_cv_right = image_sl_right.get_data()
    image_cv_left = image_sl_left.get_data()

    left_img_dest_name = "ZED_left_%s.png" % str(numset).zfill(6)
    right_img_dest_name = "ZED_right_%s.png" % str(numset).zfill(6)

    cv2.imwrite(os.path.join(dest_dir,'left', left_img_dest_name), image_cv_left)
    cv2.imwrite(os.path.join(dest_dir, 'right', right_img_dest_name), image_cv_right)

def save_depth(zed,  dest_dir, numset):
    # max_value = 65535.
    # scale_factor = max_value / zed.get_depth_max_range_value() # set up when UNIT is in Meter

    depth_sl_left = sl.Mat()
    depth_sl_right = sl.Mat()
    try:
        saved_left = zed.retrieve_measure(depth_sl_left, sl.MEASURE.MEASURE_DEPTH)
        saved_right = zed.retrieve_measure(depth_sl_right, sl.MEASURE.MEASURE_DEPTH_RIGHT)
    except:
        print("Failed... Please check that you have permissions to write on disk")
        return -1

    left_img_dest_name = "ZED_depth_left_%s.png" % str(numset).zfill(6)
    right_img_dest_name = "ZED_depth_right_%s.png" % str(numset).zfill(6)

    depth_cv_left= depth_sl_left.get_data().astype(np.uint16)
    depth_cv_right = depth_sl_right.get_data().astype(np.uint16)

    cv2.imwrite(os.path.join(dest_dir,'left', left_img_dest_name), depth_cv_left)
    cv2.imwrite(os.path.join(dest_dir, 'right', right_img_dest_name), depth_cv_right)


def save_confidence(zed, dest_dir, numset):
    depth_sl_conf = sl.Mat()
    zed.retrieve_image(depth_sl_conf, sl.VIEW.VIEW_CONFIDENCE)
    depth_cv_conf = depth_sl_conf.get_data()
    img_dest_name = "ZED_confidence_map_%s.png" % str(numset).zfill(6)
    cv2.imwrite(os.path.join(dest_dir, img_dest_name), depth_cv_conf)



if __name__ == '__main__':
    time_logger = np.zeros(8400, dtype='int')
    date_logger = np.zeros(8400, dtype='int')

    raw_dest_dir = os.path.join(__DEST_PATH__, 'RAW')
    if not os.path.exists(raw_dest_dir):
        os.makedirs(os.path.join(raw_dest_dir, 'Canon'))
        os.makedirs(os.path.join(raw_dest_dir, 'P20'))
        os.makedirs(os.path.join(raw_dest_dir, 'ZED'))

    cpr_dest_dir = os.path.join(__DEST_PATH__, 'Compressed')
    if not os.path.exists(cpr_dest_dir):
        os.makedirs(os.path.join(cpr_dest_dir, 'Canon'))
        os.makedirs(os.path.join(cpr_dest_dir, 'P20'))
        os.makedirs(os.path.join(cpr_dest_dir, 'ZED', 'color', 'left'))
        os.makedirs(os.path.join(cpr_dest_dir, 'ZED', 'color', 'right'))
        os.makedirs(os.path.join(cpr_dest_dir, 'ZED', 'depth', 'left'))
        os.makedirs(os.path.join(cpr_dest_dir, 'ZED', 'depth', 'right'))
        os.makedirs(os.path.join(cpr_dest_dir, 'ZED', 'confidence'))

    count = 0
    start_time = time.time()
    for sorted_folders in os.listdir(__PATH__):
        sorted_path = os.path.join(__PATH__, sorted_folders, 'sorted')
        for set_folders in os.listdir(sorted_path):
            count += 1
            numset = int(set_folders.split('set')[-1])
            print('====[{}] {} ===='.format(count,numset))
            if count % 50 ==0:
                elasped = time.time() - start_time
                print('({:.3f}) {}/8391'.format(elasped, count))

            set_path = os.path.join(sorted_path, set_folders)
            #print(os.listdir(set_path))
            for files in os.listdir(set_path):
                #print(files)
                '''
                # Move canon files
                if '.CR2' in files:
                    canon_img_dir = os.path.join(set_path, files)
                    canon_img_dest_name = "Canon_%s.CR2" % str(numset).zfill(6)
                    copy2(canon_img_dir, os.path.join(raw_dest_dir, 'Canon', canon_img_dest_name))
                elif '.JPG' in files:
                    canon_img_dir = os.path.join(set_path, files)
                    canon_img_dest_name = "Canon_%s.JPG" % str(numset).zfill(6)
                    copy2(canon_img_dir, os.path.join(cpr_dest_dir, 'Canon', canon_img_dest_name))
                # Move P20 files
                elif '.dng' in files:
                    p20_img_dir = os.path.join(set_path, files)
                    p20_img_dest_name = "P20_%s.dng" % str(numset).zfill(6)
                    copy2(p20_img_dir, os.path.join(raw_dest_dir, 'P20', p20_img_dest_name))
                elif '.jpg' in files:
                    #p20_img_dir = os.path.join(set_path, files)
                    #p20_img_dest_name = "P20_%s.jpg" % str(numset).zfill(6)
                    captime = files.split('IMG_')[-1].split('.jpg')[0]
                    date_logger[numset] = int(captime.split('_')[0][2:])
                    time_logger[numset] = int(captime.split('_')[1])
                    #copy2(p20_img_dir, os.path.join(cpr_dest_dir, 'P20', p20_img_dest_name))
                '''
                # Make images from zed svo
                if '.svo' in files:
                    zed_svo_dir = os.path.join(set_path, files)
                    zed_svo_dest_name = "ZED_%s.svo" % str(numset).zfill(6)
                    img_out_file = os.path.join(cpr_dest_dir, 'ZED')

                    # Create a Camera object
                    zed = sl.Camera()

                    # Create a InitParameters object and set configuration parameters
                    init_params = sl.InitParameters()
                    init_params.coordinate_units = sl.UNIT.UNIT_MILLIMETER
                    # init_params.coordinate_system=sl.COORDINATE_SYSTEM.COORDINATE_SYSTEM_RIGHT_HANDED_Y_UP,
                    init_params.camera_disable_self_calib = False
                    init_params.depth_minimum_distance = 0.5  # in meter
                    init_params.enable_right_side_measure = True
                    init_params.sdk_verbose = True
                    init_params.depth_mode = sl.DEPTH_MODE.DEPTH_MODE_ULTRA # Change this to have different depth module
                    init_params.svo_input_filename = str(zed_svo_dir)
                    init_params.svo_real_time_mode = False  # Don't convert in realtime

                    # Open the camera
                    err = zed.open(init_params)
                    if err != sl.ERROR_CODE.SUCCESS:
                        exit(1)

                    # Set runtime parameters after opening the camera
                    runtime = sl.RuntimeParameters()
                    runtime.sensing_mode = sl.SENSING_MODE.SENSING_MODE_STANDARD
                    runtime.measure3D_reference_frame = sl.REFERENCE_FRAME.REFERENCE_FRAME_WORLD

                    zed.set_depth_max_range_value(40000)

                    try:
                        if zed.grab(runtime) == sl.ERROR_CODE.SUCCESS:
                            save_rgb_zed_image(zed, os.path.join(img_out_file, 'color'), numset)
                            save_depth(zed, os.path.join(img_out_file, 'depth'), numset)
                            save_confidence(zed, os.path.join(img_out_file, 'confidence'), numset)
                    except:
                        print('Error in SET {}'.format(numset))
                    print('saved!')
                    zed.close()

                    #copy2(zed_svo_dir, os.path.join(raw_dest_dir, 'ZED', zed_svo_dest_name))

    np.savetxt(os.path.join(raw_dest_dir, 'time_img.txt'), time_logger, delimiter=' ')
    np.savetxt(os.path.join(raw_dest_dir, 'date_img.txt'), date_logger, delimiter=' ')

    print('({:.3f}) Done!'.format(time.time()-start_time))










