import cv2
import os
import time
import pyzed.sl as sl
import ffmpeg


from utils.print_utils import magenta, yellow
import utils.log_utils as logutils
import utils.zed_utils as zutils



# Set input video and output directory
input_dir = './saved_data/VID/{}/'.format(time.strftime('%Y%m%d'))
output_dir = './saved_data/VID/{}/frames'.format(time.strftime('%Y%m%d'))
log_dir = './saved_data/VID/{}/video_capture.log'.format(time.strftime('%Y%m%d'))


def check_rotation(path_video_file):
    '''
        Check the meta data of the video file and return rotation code(opencv flag)
    :param path_video_file: path to the video file
    :return: rotation code [None: no roation, cv2.ROTATE_180: when rotated 180 degree]
    '''
    # meta-data of the video file in form of a dictionary
    meta_dict = ffmpeg.probe(path_video_file)

    rotateCode = None
    # from the dictionary, meta_dict['streams'][0]['tags']['rotate'] is the key
    if 'rotate' in meta_dict['streams'][0]['tags']:
        if int(meta_dict['streams'][0]['tags']['rotate']) == 90:
            rotateCode = cv2.ROTATE_90_CLOCKWISE
        elif int(meta_dict['streams'][0]['tags']['rotate']) == 180:
            rotateCode = cv2.ROTATE_180
        elif int(meta_dict['streams'][0]['tags']['rotate']) == 270:
            rotateCode = cv2.ROTATE_90_COUNTERCLOCKWISE

    return rotateCode


def correct_rotation(frame, rotateCode):
    if rotateCode is not None:
        return cv2.rotate(frame, rotateCode)
    else:
        return frame


def videos2frames(input_video, output_folder, end_frame=1000):
    input_video_name = os.path.basename(input_video)
    input_video_name = input_video_name.split('.')[0]

    output_folder = os.path.join(output_folder, input_video_name)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    print(magenta('INPUT video name: {}'.format(input_video_name)))
    print(magenta('Saving the frames to {}'.format(output_folder)))

    rotateCode = check_rotation(input_video)

    n = 1  # every n-th frame that we want to extract as a image.

    cap = cv2.VideoCapture(input_video)

    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    print("Input video size is {:.0f}x{:.0f}".format(cap.get(3), cap.get(4)))
    print("Total number of frames is {:.0f}".format(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
    print("The FPS is {:.0f}".format(cap.get(cv2.CAP_PROP_FPS)))

    frame_number = 0

    while (cap.isOpened()):
        ret, frame = cap.read()

        # check if rotation on the frame is needed
        frame = correct_rotation(frame, rotateCode)

        # Save every n-th frames
        if (frame_number % n == 0):
            cv2.imwrite(os.path.join(output_folder, 'frame{}.png'.format(int(frame_number / n))) \
                        , frame)

            if (frame_number % 40 == 0):
                print('... Saving {:.0f}/{:.0f} frame'.format(frame_number, total_frames))

        frame_number += 1

        if frame_number == end_frame:
            print('Reaching target frame number. Exiting...')
            break

        if (frame_number >= cap.get(cv2.CAP_PROP_FRAME_COUNT)):
            break

    cap.release()
    print('Finished saving the frames')


def zed_videos2frames(input_video, output_folder, end_frame=1000):
    input_video_name = os.path.basename(input_video)
    input_video_name = input_video_name.split('.')[0]

    output_folder = os.path.join(output_folder, input_video_name)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    print(magenta('INPUT video name: {}'.format(input_video_name)))
    print(magenta('Saving the frames to {}'.format(output_folder)))

    init = sl.InitParameters(svo_input_filename=input_video,svo_real_time_mode=False)
    cam = sl.Camera()
    status = cam.open(init)
    if status != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        exit()

    runtime = sl.RuntimeParameters()
    frame_number = 1
    while True:
        if cam.grab(runtime) == sl.ERROR_CODE.SUCCESS:
            filename = output_folder + '/frame{}'.format(frame_number)
            zutils.save_rgb_image(cam, filename)
            frame_number += 1

            if frame_number == end_frame:
                print('Reaching target frame number. Exiting...')
                break
        else:
            break
    cam.close()
    print('Finished saving the frames')


if __name__ == '__main__':

    # list is in [D5, P20, ZED] order
    list_vid_dir = logutils.read_log_file(log_dir, input_dir, is_video=True)

    max_frame = 20

    for i, sets in enumerate(list_vid_dir[3:]):
        print(yellow('[Set {}]Saving to frames'.format(i)))
        output_folder= os.path.join(output_dir, 'sets{}'.format(i))
        videos2frames(sets[0], output_folder, end_frame=max_frame)
        videos2frames(sets[1], output_folder, end_frame=max_frame)
        zed_videos2frames(sets[2], output_folder, end_frame=max_frame)

    print('Done!')




