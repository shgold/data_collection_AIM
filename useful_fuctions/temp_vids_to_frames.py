import sys
import pyzed.sl as sl
import numpy as np
import cv2
from pathlib import Path
import enum
import os


def progress_bar(percent_done, bar_length=50):
    done_length = int(bar_length * percent_done / 100)
    bar = '=' * done_length + '-' * (bar_length - done_length)
    sys.stdout.write('[%s] %f%s\r' % (bar, percent_done, '%'))
    sys.stdout.flush()


def extract_zed_svofile(svo_input_path, other_frames=None):
    # Set output path to save frames
    output_path = Path(os.path.join(os.path.split(svo_input_path)[0], 'zed_frames'))
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    if other_frames is not None:
        assert other_frames =='rgb_right' or other_frames=='depth_left', 'Parameter:: other_frames = [rgb_right | depth_left]'

    # Specify SVO path parameter
    init_params = sl.InitParameters()
    init_params.svo_input_filename = str(svo_input_path)
    init_params.svo_real_time_mode = False  # Don't convert in realtime
    init_params.coordinate_units = sl.UNIT.UNIT_MILLIMETER  # Use milliliter units (for depth measurements)

    # Create ZED objects
    zed = sl.Camera()

    # Open the SVO file specified as a parameter
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        sys.stdout.write(repr(err))
        zed.close()
        exit()

    # Get image size
    image_size = zed.get_resolution()
    width = image_size.width

    # Prepare single image containers
    left_image = sl.Mat()
    right_image = sl.Mat()
    depth_image = sl.Mat()

    rt_param = sl.RuntimeParameters()
    rt_param.sensing_mode = sl.SENSING_MODE.SENSING_MODE_STANDARD

    # Start SVO conversion to AVI/SEQUENCE
    sys.stdout.write("Converting SVO... Use Ctrl-C to interrupt conversion.\n")

    nb_frames = zed.get_svo_number_of_frames()

    while True:
        if zed.grab(rt_param) == sl.ERROR_CODE.SUCCESS:
            svo_position = zed.get_svo_position()

            # Retrieve SVO images
            zed.retrieve_image(left_image, sl.VIEW.VIEW_LEFT)

            if other_frames == 'rgb_right':
                zed.retrieve_image(right_image, sl.VIEW.VIEW_RIGHT)
            elif other_frames =='depth_left':
                zed.retrieve_measure(depth_image, sl.MEASURE.MEASURE_DEPTH) # depth uint16

            # Generate file names
            filename1 = output_path / ("zed%s.png" % str(svo_position).zfill(6))

            # Save Left images
            cv2.imwrite(str(filename1), left_image.get_data())

            if other_frames is not None:
                filename2 = output_path / (("right%s.png" if other_frames == 'rgb_right'
                                           else "depth%s.png") % str(svo_position).zfill(6))
                if other_frames == 'rgb_right':
                    # Save right images
                    cv2.imwrite(str(filename2), right_image.get_data())
                else:
                    # Save depth images (convert to uint16)
                    cv2.imwrite(str(filename2), depth_image.get_data().astype(np.uint16))

            # Display progress
            progress_bar((svo_position + 1) / nb_frames * 100, 30)

            # Check if we have reached the end of the video
            if svo_position >= (nb_frames - 1):  # End of SVO
                sys.stdout.write("\nSVO end has been reached. Exiting now.\n")
                break

    zed.close()
    return 0


def extract_canon_videos(canon_input_path):
    # Set output path to save frames
    output_path = Path(os.path.join(os.path.split(canon_input_path)[0], 'canon_frames'))
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    n = 1  # every n-th frame that we want to extract as a image.

    cap = cv2.VideoCapture(canon_input_path)

    print("Input video size is {:.0f}x{:.0f}".format(cap.get(3), cap.get(4)))
    print("Total number of frames is {:.0f}".format(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
    print("The FPS is {:.0f}".format(cap.get(cv2.CAP_PROP_FPS)))

    frame_number = 0
    nb_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    while (cap.isOpened()):
        ret, frame = cap.read()

        # Save every n-th frames
        if (frame_number % n == 0):
            # Generate file names
            filename = output_path / ("canon%s.png" % str(frame_number).zfill(6))
            cv2.imwrite(str(filename), frame)

        # Display progress
        progress_bar((frame_number + 1) / nb_frames * 100, 30)

        frame_number += 1

        if (frame_number >= nb_frames): # End of frames
            sys.stdout.write("\nCanon video end has been reached. Exiting now.\n")
            break

    cap.release()
    return 0

if __name__ == "__main__":

    __INPUT_DIR__ = '/media/dc2019/My Book/VID/RAW/training/'

    set_list = os.listdir(__INPUT_DIR__)

    for set in set_list:
        print('===> Converting videos in {}'.format(set))
        base_dir = os.path.join(__INPUT_DIR__, set)

        if len(os.listdir(base_dir)) == 5:
            print('passing...{}'.format(set))
            continue

        files = os.listdir(base_dir)
        zed_vid_dir = None
        canon_vid_dir = None
        for f in files:
            if '.svo' in f:
                zed_vid_dir= os.path.join(base_dir, f)
            elif '.MOV' in f:
                canon_vid_dir = os.path.join(base_dir, f)

        extract_zed_svofile(zed_vid_dir)
        extract_canon_videos(canon_vid_dir)

    