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

def measure_depth(event, y, x, flags, param):
    global mouseX, mouseY
    if event == cv2.EVENT_LBUTTONDOWN:
        depth = depth_sl_left.get_value(x,y, sl.MEM.MEM_CPU)
        print (x,y, depth)
        mouseX = x
        mouseY = y
        return mouseX, mouseY


# Checks if a matrix is a valid rotation matrix.
def isRotationMatrix(R):
    print(R)
    Rt = np.transpose(R)
    shouldBeIdentity = np.dot(Rt, R)
    I = np.identity(3, dtype=R.dtype)
    n = np.linalg.norm(I - shouldBeIdentity)
    return n < 1e-6

def isclose(x, y, rtol=1.e-5, atol=1.e-8):
    return abs(x-y) <= atol + rtol * abs(y)

# Calculates rotation matrix to euler angles
# The result is the same as MATLAB except the order
# of the euler angles ( x and z are swapped ).
def rotationMatrixToEulerAngles(R):
    # assert (isRotationMatrix(R))

    sy = math.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])

    singular = sy < 1e-6

    if not singular:
        x = math.atan2(R[2, 1], R[2, 2])
        y = math.atan2(-R[2, 0], sy)
        z = math.atan2(R[1, 0], R[0, 0])
    else:
        x = math.atan2(-R[1, 2], R[1, 1])
        y = math.atan2(-R[2, 0], sy)
        z = 0

    phi = 0.0
    if isclose(R[2,0],-1.0):
        theta = math.pi/2.0
        psi = math.atan2(R[0,1],R[0,2])
    elif isclose(R[2,0],1.0):
        theta = -math.pi/2.0
        psi = math.atan2(-R[0,1],-R[0,2])
    else:
        theta = -math.asin(R[2,0])
        cos_theta = math.cos(theta)
        psi = math.atan2(R[2,1]/cos_theta, R[2,2]/cos_theta)
        phi = math.atan2(R[1,0]/cos_theta, R[0,0]/cos_theta)
    return np.array([[psi, theta, phi], [x, y, z]])
    # return np.array([x, y, z])


def eulerAnglesToRotationMatrix(theta):
    R_x = np.array([[1, 0, 0],
                    [0, math.cos(theta[0]), -math.sin(theta[0])],
                    [0, math.sin(theta[0]), math.cos(theta[0])]
                    ])

    R_y = np.array([[math.cos(theta[1]), 0, math.sin(theta[1])],
                    [0, 1, 0],
                    [-math.sin(theta[1]), 0, math.cos(theta[1])]
                    ])

    R_z = np.array([[math.cos(theta[2]), -math.sin(theta[2]), 0],
                    [math.sin(theta[2]), math.cos(theta[2]), 0],
                    [0, 0, 1]
                    ])

    R = np.dot(R_z, np.dot(R_y, R_x))

    return R


def plot_translation_values(translation):
    x  = translation[0]
    y = translation[1]
    z = translation[2]

    fig = plt.figure()
    ax = plt.axes(projection='3d')

    def update(frame):
        x_data.append(datetime.now())
        y_data.append(randrange(0, 100))
        line.set_data(x_data, y_data)
        figure.gca().relim()
        figure.gca().autoscale_view()
        return line,



if __name__ == '__main__':
    global depth_sl_left
    print('Starting...')

    # Configure zed camera
    zed, runtime = zutils.configure_zed_camera(svo_file='./saved_data/VID/20190615/sorted_part1/set17/ZED_VID_20190615152052.svo')

    cv2.namedWindow('rgb', cv2.WINDOW_NORMAL)
    cv2.namedWindow('depth', cv2.WINDOW_NORMAL)
    cv2.setMouseCallback('rgb', measure_depth)

    count = 0
    key =' '
    while key != 113:
        if zed.grab(runtime) == sl.ERROR_CODE.SUCCESS:


            depth_sl_left16 = sl.Mat()
            saved_left = zed.retrieve_measure(depth_sl_left16, sl.MEASURE.MEASURE_DEPTH)
            depth_left16 = depth_sl_left16.get_data().astype(np.uint16)


            depth_sl_left = sl.Mat()
            zed.retrieve_image(depth_sl_left, sl.VIEW.VIEW_DEPTH)
            depth_cv_left = depth_sl_left.get_data()

            rgb_sl_left =sl.Mat()
            saved_rgbleft = zed.retrieve_image(rgb_sl_left, sl.VIEW.VIEW_RIGHT)
            rgb_cv_left = rgb_sl_left.get_data()
            print(depth_left16.shape)

            cv2.imshow('rgb', rgb_cv_left)
            cv2.imshow('depth', depth_cv_left)
            count+=1
            #zutils.save_unrectified_rgb_image(zed, '../test/unrectified/{}'.format(count))
            #zutils.save_rgb_image(zed, '../test/rectified/{}'.format(count))
            #zutils.save_depth(zed, '../test/depth/{}'.format(count))

            # camera pose
            camera_pose = sl.Pose()
            zed.get_position(camera_pose, sl.REFERENCE_FRAME.REFERENCE_FRAME_WORLD)
            euler_angle = camera_pose.get_euler_angles(radian=True)
            orientation = camera_pose.get_orientation().get()
            rot_matrix = camera_pose.get_rotation_matrix()
            rot_vector = camera_pose.get_rotation_vector()
            translation = camera_pose.get_translation().get()

            key = cv2.waitKey(10)

            #if key == 109: # key for 'm'
            print('===============frame [{}] =================='.format(count))
            print('Current frame fps:', zed.get_current_fps())
            print('Euler angle', np.around(euler_angle, 3))
            print('Orientation', np.around(orientation,3))
            print('Translation', np.around(translation,3))
            print('Rotation vector', np.around(rot_vector,3))
            print('Rotation matrix', np.around(rot_matrix.r, 3))
            print('Euler to RotMat', eulerAnglesToRotationMatrix(euler_angle))
            print('RotMat to Euler angle', rotationMatrixToEulerAngles(rot_matrix.r))
            print('====================================')

        else:
            break

    cv2.destroyAllWindows()
    zed.disable_spatial_mapping()
    zed.disable_tracking()
    zed.close()
    print('Done!')

