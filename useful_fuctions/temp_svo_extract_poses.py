import sys
import pyzed.sl as sl
import numpy as np
import cv2
from pathlib import Path
import enum
import os
import utils.zed_utils as zutils



def progress_bar(percent_done, bar_length=50):
    done_length = int(bar_length * percent_done / 100)
    bar = '=' * done_length + '-' * (bar_length - done_length)
    sys.stdout.write('[%s] %f%s\r' % (bar, percent_done, '%'))
    sys.stdout.flush()


def save_parameters(zed, filename):
    print("Saving parameters of the camera >>> ", filename)

    def get_camera_parameters(cam_calibration):

        res_param={}

        left = cam_calibration.left_cam
        right= cam_calibration.right_cam

        # Save focal length (in pixel)
        res_param['focal_length'] ={}
        res_param['focal_length']['left'] = [left.fx, left.fy]
        res_param['focal_length']['right'] = [right.fx, right.fy]

        # Save distortion factor
        res_param['distortion_factor'] = {}
        res_param['distortion_factor']['left'] = left.disto
        res_param['distortion_factor']['right'] = right.disto

        # Optical center (in pixel)
        res_param['optical_center'] = {}
        res_param['optical_center']['left'] = [left.cx, left.cy]
        res_param['optical_center']['right'] = [right.cx, right.cy]

        # Save field of view (in degrees) [diagonal, horizontal, vertical]
        res_param['fov'] = {}
        res_param['fov']['left'] = [left.d_fov, left.h_fov, left.v_fov]
        res_param['fov']['right'] = [right.d_fov, right.h_fov, right.v_fov]

        # Save extrinsic parameters between two sensors
        res_param['Rotation'] = cam_calibration.R
        res_param['Translation'] = cam_calibration.T

        return res_param

    cam_param= {}

    # Save image information
    cam_param['resolution'] = zed.get_resolution()
    cam_param['fps'] = zed.get_current_fps()
    cam_param['timestamp'] = zed.get_timestamp(sl.TIME_REFERENCE.TIME_REFERENCE_IMAGE)
    cam_param['confidence_threshold'] = zed.get_confidence_threshold()
    cam_param['depth_range'] =[zed.get_depth_min_range_value(), zed.get_depth_max_range_value()]


    # Save camera settings
    # More details refer here:
    # file:///home/sokim/Desktop/data_collection/zed-python-api/doc/build/html/video.html?highlight=auto%20white%20balance#pyzed.sl.CAMERA_SETTINGS
    gain = zed.get_camera_settings(sl.CAMERA_SETTINGS.CAMERA_SETTINGS_GAIN)
    brightness = zed.get_camera_settings(sl.CAMERA_SETTINGS.CAMERA_SETTINGS_BRIGHTNESS)
    contrast = zed.get_camera_settings(sl.CAMERA_SETTINGS.CAMERA_SETTINGS_CONTRAST)
    exposure = zed.get_camera_settings(sl.CAMERA_SETTINGS.CAMERA_SETTINGS_EXPOSURE)
    hue = zed.get_camera_settings(sl.CAMERA_SETTINGS.CAMERA_SETTINGS_HUE)
    saturation = zed.get_camera_settings(sl.CAMERA_SETTINGS.CAMERA_SETTINGS_SATURATION)
    whitebalance = zed.get_camera_settings(sl.CAMERA_SETTINGS.CAMERA_SETTINGS_WHITEBALANCE)

    cam_param['settings'] = [gain, brightness, contrast, exposure, hue, saturation, whitebalance]

    # Save camera intrinsic and extrinsic parameters
    cam_info_raw = zed.get_camera_information().calibration_parameters_raw
    cam_info= zed.get_camera_information().calibration_parameters

    cam_param['unrectified'] = get_camera_parameters(cam_info_raw)
    cam_param['rectified'] = get_camera_parameters(cam_info)

    # Save camera position
    camera_pose = sl.Pose()
    zed.get_position(camera_pose, sl.REFERENCE_FRAME.REFERENCE_FRAME_WORLD)
    cam_param['euler_angle'] = camera_pose.get_euler_angles(radian=True)
    cam_param['quaternion_orientation'] = camera_pose.get_orientation().get()
    cam_param['rotation_matrix'] = camera_pose.get_rotation_matrix().r
    cam_param['rodrigues_rotation'] = camera_pose.get_rotation_vector()
    cam_param['camera_position'] = camera_pose.get_translation().get()

    with open(filename +'_param.txt', 'w') as file:
        file.write(str(cam_param))
#    np.save(filename +'_param.npy', np.asarray(cam_param)


def extract_zed_svofile(svo_input_path, output_path, other_frames=None):
    # Set output path to save frames
    output_path = Path(output_path)
    if not os.path.exists(output_path / 'left'):
        os.makedirs(output_path / 'left')

    if other_frames is not None:
        assert other_frames =='rgb_right' or other_frames=='depth_left', 'Parameter:: other_frames = [rgb_right | depth_left]'

    zed, runtime = zutils.configure_zed_camera(img_capture=False, svo_file=svo_input_path)

    # Start SVO conversion to AVI/SEQUENCE
    sys.stdout.write("Converting SVO... Use Ctrl-C to interrupt conversion.\n")

    nb_frames = zed.get_svo_number_of_frames()
    # Prepare single image containers
    left_image = sl.Mat()
    right_image = sl.Mat()
    depth_image = sl.Mat()
    camera_pose = sl.Pose()
    pose_filename = output_path / 'pose.txt'
    calib_filename = output_path / 'calib.txt'

    with open(pose_filename, 'w') as file:
        while True:
            if zed.grab(runtime) == sl.ERROR_CODE.SUCCESS:
                svo_position = zed.get_svo_position()

                #Retrieve SVO images
                zed.retrieve_image(left_image, sl.VIEW.VIEW_LEFT)

                if other_frames == 'rgb_right':
                    zed.retrieve_image(right_image, sl.VIEW.VIEW_RIGHT)
                elif other_frames =='depth_left':
                    zed.retrieve_measure(depth_image, sl.MEASURE.MEASURE_DEPTH) # depth uint16

                # Generate file names
                filename1 = output_path/'left' / ("%s.png" % str(svo_position-1).zfill(6))

                # Save Left images
                cv2.imwrite(str(filename1), left_image.get_data())

                if other_frames is not None:
                    if other_frames == 'rgb_right':
                        if not os.path.exists(output_path / 'right'):
                            os.makedirs(output_path / 'right')
                        # Save right images
                        filename2 = output_path / 'right' / ("%s.png" % str(svo_position-1).zfill(6))
                        cv2.imwrite(str(filename2), right_image.get_data())
                    else:
                        if not os.path.exists(output_path / 'depth'):
                            os.makedirs(output_path / 'depth')
                        # Save depth images (convert to uint16)
                        filename2 = output_path / 'depth' /("%s.png" % str(svo_position-1).zfill(6))
                        cv2.imwrite(str(filename2), depth_image.get_data().astype(np.uint16))

                # Save pose data into txt file
                zed.get_position(camera_pose, sl.REFERENCE_FRAME.REFERENCE_FRAME_WORLD)
                rotation_matrix = camera_pose.get_rotation_matrix().r
                translation = camera_pose.get_translation().get()
                #print(rotation_matrix)
                #print(translation)
                RT = np.hstack((rotation_matrix, translation.reshape((3,1))))
                # cam_param['euler_angle'] = camera_pose.get_euler_angles(radian=True)
                # cam_param['quaternion_orientation'] = camera_pose.get_orientation().get()
                # cam_param['rotation_matrix'] = camera_pose.get_rotation_matrix().r
                # cam_param['rodrigues_rotation'] = camera_pose.get_rotation_vector()
                # cam_param['camera_position'] = camera_pose.get_translation().get()
                file.write(",".join(map(str, RT.reshape(-1))) + "\n")


                cam_param = zed.get_camera_information().calibration_parameters.left_cam
                fx, fy = cam_param.fx, cam_param.fy
                cx, cy = cam_param.cx, cam_param.cy
                np.savetxt(calib_filename, (fx,fy, cx,cy))

                # Display progress
                progress_bar((svo_position + 1) / nb_frames * 100, 30)

                # Check if we have reached the end of the video
                if svo_position >= (nb_frames - 1):  # End of SVO
                    sys.stdout.write("\nSVO end has been reached. Exiting now.\n")
                    break

    zed.close()
    return 0


if __name__ == "__main__":

    __INPUT_DIR__ = '/media/dc2019/My Book/VID/00_RAW/test/'
    __OUTPUT_DIR__ = '/media/dc2019/My Book/VID/Thesis_data/test'
    #__INPUT_DIR__ = './saved_data/VID/'

    set_list = os.listdir(__INPUT_DIR__)

    for set in set_list[1:]:
        print('===> Converting videos in {}'.format(set))
        base_dir = os.path.join(__INPUT_DIR__, set)
        out_dir = os.path.join(__OUTPUT_DIR__, set)

        if len(os.listdir(base_dir)) == 5:
            print('passing...{}'.format(set))
            continue

        files = os.listdir(base_dir)
        zed_vid_dir = None
        canon_vid_dir = None
        for f in files:
            if '.svo' in f:
                zed_vid_dir= os.path.join(base_dir, f)

        extract_zed_svofile(zed_vid_dir, out_dir, other_frames='depth_left')

    