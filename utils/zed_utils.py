import sys
import numpy as np
import pyzed.sl as sl
import cv2
import pickle

# help_string = "[s] Save side by side image [d] Save Depth, [n] Change Depth format, [p] Save Point Cloud, [m] Change Point Cloud format, [q] Quit"
# prefix_point_cloud = "Cloud_"
# prefix_depth = "Depth_"
# path = "../saved_data/"
#
# count_save = 0
# mode_point_cloud = 0
# mode_depth = 0
# point_cloud_format = sl.POINT_CLOUD_FORMAT.POINT_CLOUD_FORMAT_XYZ_ASCII
# depth_format = sl.DEPTH_FORMAT.DEPTH_FORMAT_PNG


def configure_zed_camera(img_capture=True, svo_file=None):
    '''
        Configure zed camera according to the capturing mode.
        - When capturing images, it will be configured in 2k@15fps + DEPTH_MODE_ULTRA.
            Also position tracking/spatial mapping will be enabled to store camera's parameters.
        - When capturing videos, it will be configured in 1080HD@30fps + DEPTH_MODE_NONE.

    :param img_capture: Flag of the image capturing mode. Default is True. When set False, it will configured as video capturing mode.
    :param svo_file: When given as a .svo file, it will configured as reading file mode.
    :return: configured zed camera object, runtime parameters

    '''
    # Create a Camera object
    zed = sl.Camera()

    # Create a InitParameters object and set configuration parameters
    init_params = sl.InitParameters()
    init_params.coordinate_units=sl.UNIT.UNIT_MILLIMETER
    # init_params.coordinate_system=sl.COORDINATE_SYSTEM.COORDINATE_SYSTEM_RIGHT_HANDED_Y_UP,
    init_params.camera_disable_self_calib = False
    init_params.depth_minimum_distance=0.5 #in meter
    init_params.enable_right_side_measure = True
    init_params.sdk_verbose=True

    if not img_capture:
        init_params.camera_resolution = sl.RESOLUTION.RESOLUTION_HD1080
        init_params.camera_fps = 30
        init_params.depth_mode = sl.DEPTH_MODE.DEPTH_MODE_NONE
    else:
        init_params.camera_resolution = sl.RESOLUTION.RESOLUTION_HD2K
        init_params.camera_fps = 15
        init_params.depth_mode = sl.DEPTH_MODE.DEPTH_MODE_NONE

    if svo_file is not None:
        init_params.depth_mode = sl.DEPTH_MODE.DEPTH_MODE_ULTRA
        init_params.svo_input_filename = str(svo_file)
        init_params.svo_real_time_mode = False  # Don't convert in realtime

    # Open the camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        exit(1)

    if svo_file is not None:
        # Positional tracking needs to be enabled before using spatial mapping
        transform = sl.Transform()
        tracking_parameters=sl.TrackingParameters(transform)
        err = zed.enable_tracking(tracking_parameters)
        if err != sl.ERROR_CODE.SUCCESS :
            exit(-1)

        # Enable spatial mapping
        mapping_parameters=sl.SpatialMappingParameters()
        err = zed.enable_spatial_mapping(mapping_parameters)
        if err != sl.ERROR_CODE.SUCCESS :
            exit(-1)

    # Get camera information (ZED serial number)
    zed_serial = zed.get_camera_information().serial_number
    print("Hello! This is my serial number: {0}".format(zed_serial))

    # Set runtime parameters after opening the camera
    runtime = sl.RuntimeParameters()
    runtime.sensing_mode = sl.SENSING_MODE.SENSING_MODE_STANDARD
    runtime.measure3D_reference_frame = sl.REFERENCE_FRAME.REFERENCE_FRAME_WORLD

    return zed, runtime


def save_point_cloud(zed, filename):
    print("Saving Point Cloud...")
    saved = sl.save_camera_point_cloud_as(zed, sl.POINT_CLOUD_FORMAT.POINT_CLOUD_FORMAT_PLY_ASCII, filename, True)
    if saved:
        print("Done")
    else:
        print("Failed... Please check that you have permissions to write on disk")


def save_depth(zed, filename):
    max_value = 65535.
    scale_factor = max_value / zed.get_depth_max_range_value() # set up when UNIT is in Meter

    print("Saving Depth Map >>> ", filename)
    depth_sl_left = sl.Mat()
    depth_sl_right = sl.Mat()
    try:
        saved_left = zed.retrieve_measure(depth_sl_left, sl.MEASURE.MEASURE_DEPTH)
        saved_right = zed.retrieve_measure(depth_sl_right, sl.MEASURE.MEASURE_DEPTH_RIGHT)
    except:
        print("Failed... Please check that you have permissions to write on disk")
        return -1

    depth_cv_left= depth_sl_left.get_data().astype(np.uint16)
    cv2.imwrite(filename + '_depth_left.png', depth_cv_left)

    depth_cv_right = depth_sl_right.get_data().astype(np.uint16)
    cv2.imwrite(filename + '_depth_right.png', depth_cv_right)


def save_rgb_image(zed, filename):
    print("Saving Color Image >>> ", filename)
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
    cv2.imwrite(filename+'_left.png', image_cv_left)
    cv2.imwrite(filename+'_right.png', image_cv_right)


def save_unrectified_rgb_image(zed, filename):
    print("Saving unrectified Color Image >>> ", filename)
    image_sl_left_unrectified = sl.Mat()
    image_sl_right_unrectified = sl.Mat()
    try:
        zed.retrieve_image(image_sl_left_unrectified, sl.VIEW.VIEW_LEFT_UNRECTIFIED)
        zed.retrieve_image(image_sl_right_unrectified, sl.VIEW.VIEW_RIGHT_UNRECTIFIED)
    except:
        print("Failed... Please check that you have permissions to write on disk")
        return -1

    image_cv_left_unrectified = image_sl_left_unrectified.get_data()
    image_cv_right_unrectified = image_sl_right_unrectified.get_data()

    cv2.imwrite(filename+'_unrectified_left.png', image_cv_left_unrectified)
    cv2.imwrite(filename+'_unrectified_right.png', image_cv_right_unrectified)


def save_other_image(zed, filename):
    print("Saving depth confidence >>> ", filename)
    depth_sl_conf = sl.Mat()
    zed.retrieve_image(depth_sl_conf, sl.VIEW.VIEW_CONFIDENCE)
    depth_cv_conf = depth_sl_conf.get_data()

    cv2.imwrite(filename+'_confidence.png', depth_cv_conf)

    # If surface normal is needed, uncomment the following lines
    # print("Saving depth surface normal ...", filename)
    # depth_sl_normal_left = sl.Mat()
    # zed.retrieve_image(depth_sl_normal_left, sl.VIEW.VIEW_NORMALS)
    # depth_cv_normal_left = depth_sl_normal_left.get_data()
    #
    # depth_sl_normal_right = sl.Mat()
    # zed.retrieve_image(depth_sl_normal_right, sl.VIEW.VIEW_NORMALS_RIGHT)
    # depth_cv_normal_right = depth_sl_normal_right.get_data()
    #
    # cv2.imwrite(filename + '_normal_left.png', depth_cv_normal_left)
    # cv2.imwrite(filename + '_normal_right.png', depth_cv_normal_right)


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


def get_params_from_txt_file(txt_file):
    with open(txt_file) as file:
        content = file.read()

    split_res = content.split('settings\': [')[1]
    split_res = split_res.split(']')[0]
    split_res = split_res.split(',')

    params = [int(i) for i in split_res]

    return params

def get_depth_format_name(f):
    if f == sl.DEPTH_FORMAT.DEPTH_FORMAT_PNG:
        return "PNG"
    elif f == sl.DEPTH_FORMAT.DEPTH_FORMAT_PFM:
        return "PFM"
    elif f == sl.DEPTH_FORMAT.DEPTH_FORMAT_PGM:
        return "PGM"
    else:
        return ""


def get_point_cloud_format_name(f):
    if f == sl.POINT_CLOUD_FORMAT.POINT_CLOUD_FORMAT_XYZ_ASCII:
        return "XYZ"
    elif f == sl.POINT_CLOUD_FORMAT.POINT_CLOUD_FORMAT_PCD_ASCII:
        return "PCD"
    elif f == sl.POINT_CLOUD_FORMAT.POINT_CLOUD_FORMAT_PLY_ASCII:
        return "PLY"
    elif f == sl.POINT_CLOUD_FORMAT.POINT_CLOUD_FORMAT_VTK_ASCII:
        return "VTK"
    else:
        return ""

def save_sbs_image(zed, filename):
    print("Saving Color Image ...", filename)
    image_sl_left = sl.Mat()
    zed.retrieve_image(image_sl_left, sl.VIEW.VIEW_LEFT)
    image_cv_left = image_sl_left.get_data()

    image_sl_right = sl.Mat()
    zed.retrieve_image(image_sl_right, sl.VIEW.VIEW_RIGHT)
    image_cv_right = image_sl_right.get_data()

    sbs_image = np.concatenate((image_cv_left, image_cv_right), axis=1)
    print(sbs_image.shape)
    cv2.imwrite(filename, sbs_image)


def process_key_event(zed, key):
    global mode_depth
    global mode_point_cloud
    global count_save
    global depth_format
    global point_cloud_format

    if key == 100 or key == 68:
        save_depth(zed, path + prefix_depth + str(count_save))
        count_save += 1
    elif key == 110 or key == 78:
        mode_depth += 1
        depth_format = sl.DEPTH_FORMAT(mode_depth % 3)
        print("Depth format: ", get_depth_format_name(depth_format))
    elif key == 112 or key == 80:
        save_point_cloud(zed, path + prefix_point_cloud + str(count_save))
        count_save += 1
    elif key == 109 or key == 77:
        mode_point_cloud += 1
        point_cloud_format = sl.POINT_CLOUD_FORMAT(mode_point_cloud % 4)
        print("Point Cloud format: ", get_point_cloud_format_name(point_cloud_format))
    elif key == 104 or key == 72:
        print(help_string)
    elif key == 115:
        save_sbs_image(zed, path + "ZED_image" + str(count_save) + ".png")
        count_save += 1
    elif key == 116:
        save_parameters(zed, path + "ZED_param" + str(count_save) + ".txt")
    else:
        a = 0


def print_help():
    print(" Press 's' to save Side by side images")
    print(" Press 'p' to save Point Cloud")
    print(" Press 'd' to save Depth image")
    print(" Press 'm' to switch Point Cloud format")
    print(" Press 'n' to switch Depth format")


def main():
    # # Create a ZED camera object
    # zed = sl.Camera()
    #
    # # Set configuration parameters
    # # init = sl.InitParameters()
    # # Create a InitParameters object and set configuration parameters
    # init = sl.InitParameters(camera_resolution=sl.RESOLUTION.RESOLUTION_HD1080,
    #                                 camera_fps=30,
    #                                 coordinate_units=sl.UNIT.UNIT_MILLIMETER,
    #                                 coordinate_system=sl.COORDINATE_SYSTEM.COORDINATE_SYSTEM_RIGHT_HANDED_Y_UP,
    #                                 depth_mode=sl.DEPTH_MODE.DEPTH_MODE_ULTRA,
    #                                 camera_disable_self_calib= False,
    #                                 depth_minimum_distance=0.3, #in meter
    #                                 enable_right_side_measure = True,
    #                                 sdk_verbose=True)
    #
    # init.save('initParameters.txt')
    #
    # if len(sys.argv) >= 2:
    #     init.svo_input_filename = sys.argv[1]
    #
    # # Open the camera
    # err = zed.open(init)
    # if err != sl.ERROR_CODE.SUCCESS:
    #     print(repr(err))
    #     zed.close()
    #     exit(1)
    #
    # # Display help in console
    # print_help()
    #
    # # Set runtime parameters after opening the camera
    # runtime = sl.RuntimeParameters()
    # runtime.sensing_mode = sl.SENSING_MODE.SENSING_MODE_STANDARD

    zed, runtime = configure_zed_camera()

    # Prepare new image size to retrieve half-resolution images
    image_size = zed.get_resolution()
    new_width = image_size.width / 2
    new_height = image_size.height / 2

    # Declare your sl.Mat matrices
    image_zed = sl.Mat() #new_width, new_height, sl.MAT_TYPE.MAT_TYPE_8U_C4)
    depth_image_zed = sl.Mat() #new_width, new_height, sl.MAT_TYPE.MAT_TYPE_8U_C4)
    point_cloud = sl.Mat()

    key = ' '
    while key != 113:
        err = zed.grab(runtime)
        if err == sl.ERROR_CODE.SUCCESS:
            # Retrieve the left image, depth image in the half-resolution
            zed.retrieve_image(image_zed, sl.VIEW.VIEW_LEFT)#, sl.MEM.MEM_CPU, int(new_width), int(new_height))
            zed.retrieve_image(depth_image_zed, sl.VIEW.VIEW_DEPTH) #, sl.MEM.MEM_CPU, int(new_width), int(new_height))
            # Retrieve the RGBA point cloud in half resolution
            zed.retrieve_measure(point_cloud, sl.MEASURE.MEASURE_XYZRGBA, sl.MEM.MEM_CPU, int(new_width),
                                 int(new_height))

            # To recover data from sl.Mat to use it with opencv, use the get_data() method
            # It returns a numpy array that can be used as a matrix with opencv
            image_ocv = image_zed.get_data()
            depth_image_ocv = depth_image_zed.get_data()

            cv2.imshow("Image", image_ocv)
            cv2.imshow("Depth", depth_image_ocv)

            key = cv2.waitKey(10)

            process_key_event(zed, key)

    cv2.destroyAllWindows()
    zed.close()

    print("\nFINISH")
#
# if __name__ == "__main__":
#     main()
