from pynput.mouse import Listener
import os
import time
from multiprocessing import Pool, Process, cpu_count
from utils.print_utils import yellow
import utils.canon_utils as canon
import utils.zed_utils as zutils

import math

import pyzed.sl as sl
import cv2
import numpy as np

__OUT_DIR__ = './test_data/depth_measurement_test/'
__SET__ = 2

global depth_nearby
global zed, __CLICK__

__CLICK__ = 0

def measure_depth(event, y, x, flags, param):
    global mouseX, mouseY, __CLICK__
    if event == cv2.EVENT_LBUTTONDOWN:
        print ('pixel', x,y, depth_sl_left.get_value(x,y, sl.MEM.MEM_CPU))

        depth_nearby ={}
        pixels_nearby = [[x,y],[x, y-1], [x, y+1], [x+1, y], [x+1, y+1], [x+1, y-1], [x-1, y], [x-1, y-1],[x-1, y+1]]
        for px, py in pixels_nearby:
            depth_nearby[px,py] = depth_sl_left.get_value(px,py, sl.MEM.MEM_CPU)

        save_dir = os.path.join(__OUT_DIR__, 'scene{}/{}/'.format(__SET__, __CLICK__))

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        print(save_dir)

        zutils.save_rgb_image(zed, save_dir)
        zutils.save_depth(zed, save_dir)
        np.save(os.path.join(save_dir, "depth_measure.npy"), depth_nearby)

        mouseX = x
        mouseY = y

        __CLICK__ +=1
        return mouseX, mouseY, depth_nearby


if __name__ == '__main__':
    global depth_sl_left, rgb_cv_left, save_dir
    set = 1
    print('Starting...')

    # Configure zed camera
    zed, runtime = zutils.configure_zed_camera(img_capture=True)

    cv2.namedWindow('rgb', cv2.WINDOW_KEEPRATIO)
    #cv2.namedWindow('depth', cv2.WINDOW_NORMAL)

    key =' '
    while key != 113: # q key
        if zed.grab(runtime) == sl.ERROR_CODE.SUCCESS:

            depth_sl_left = sl.Mat()
            saved_depth_left = zed.retrieve_measure(depth_sl_left, sl.MEASURE.MEASURE_DEPTH)
            #depth_sl_left = saved_depth_left.get_data().astype(np.uint16)

            rgb_sl_left =sl.Mat()
            saved_rgbleft = zed.retrieve_image(rgb_sl_left, sl.VIEW.VIEW_LEFT)
            rgb_cv_left = rgb_sl_left.get_data()

            cv2.imshow('rgb', rgb_cv_left)
            cv2.setMouseCallback('rgb', measure_depth)

            #zutils.save_unrectified_rgb_image(zed, '../test/unrectified/{}'.format(count))

            key = cv2.waitKey(5)




    cv2.destroyAllWindows()
    zed.disable_spatial_mapping()
    zed.disable_tracking()
    zed.close()
    print('Done!')