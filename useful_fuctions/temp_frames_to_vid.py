import io
import os
import subprocess
from multiprocessing import Pool
from shutil import copy2

magenta = lambda text: '\033[0;35m' + text + '\033[0m'


def read_frame_flags(txt_dir):
    '''
        Reat the 'frame_flag.txt' file and parse the info into a dictionary
    :param txt_dir:
    :return: A dictionary set_info={'type': (str) or data type,
                                    'canon: (str) starting frame of the canon,
                                    'zed': (str) starting frame of the zed,
                                    'cam_moving': (bool) whether camera is moving}
    '''

    set_info = {}
    with open(txt_dir, 'r') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line in ['training', 'validation', 'test']:
                set_info['type'] = line
            elif 'canon' in line:
                set_info['canon'] = line.split(':')[-1]
            elif 'zed' in line:
                set_info['zed'] = line.split(':')[-1]
            elif line == 'camera_moving':
                set_info['cam_moving'] = True
            elif 'None' == line:
                set_info = None
                break

    return set_info


def encode_video(cmd):
    # parse the cmd
    starting_frame, frame_name, total_frame_number, output_video = cmd

    return subprocess.call(['ffmpeg', '-start_number', starting_frame ,'-i', frame_name, '-vframes', str(total_frame_number),
                         '-r', '30', '-b:v', '64M', '-vcodec', 'libx265', output_video])

def copy_frames_to(cmd):
    src_dir = cmd[0]
    tgt_dir = cmd[1]
    copy2(src_dir, tgt_dir)
    return 0

if __name__ == "__main__":

    __INPUT_DIR__ = '/media/dc2019/My Book/VID/RAW/testing_this/'#'/media/dc2019/My Book/VID/00_RAW/test/'
    __OUTPUT_DIR__ = '/media/dc2019/My Book/VID/VQM_data'
    target_sec = 50 # target seconds for the video

    set_continue = 50
    val_set_continue = 16
    test_set_continue = 14

    set_list = sorted(os.listdir(__INPUT_DIR__))

    for set in set_list:
        print('===> Now encoding.... {}'.format(set))
        base_dir = os.path.join(__INPUT_DIR__, set)
        zed_frame_dir = os.path.join(base_dir, 'zed_frames')
        canon_frame_dir = os.path.join(base_dir, 'canon_frames')

        frame_flag_info = read_frame_flags(os.path.join(base_dir, 'frame_flag.txt'))
        if frame_flag_info is None:
            continue
        zed_starting_frame = frame_flag_info['zed'] #str
        canon_starting_frame = frame_flag_info['canon'] #str

        # Compute the total number of frame of the video
        zed_frame_num = len(os.listdir(zed_frame_dir))
        canon_frame_num = len(os.listdir(canon_frame_dir))
        total_frame_number = min(30*target_sec, min((canon_frame_num - int(canon_starting_frame)), (zed_frame_num - int(zed_starting_frame))))

        # Set the input frames and output video
        canon_frames = os.path.join(canon_frame_dir, 'canon%06d.png')
        zed_frames = os.path.join(zed_frame_dir, 'zed%06d.png')

        pool = Pool(processes=2)

        if frame_flag_info['type'] == 'training':
            print(magenta('[Training SET] Total frame numbers to be used {}'.format(total_frame_number)))

            canon_output_video = os.path.join(__OUTPUT_DIR__, 'canon/training/set{:02d}.mp4'.format(set_continue))
            zed_output_video = os.path.join(__OUTPUT_DIR__, 'zed/training/set{:02d}.mp4'.format(set_continue))

            canon_cmd = [canon_starting_frame, canon_frames, total_frame_number, canon_output_video]
            zed_cmd = [zed_starting_frame, zed_frames, total_frame_number, zed_output_video]

            pool.map(encode_video, [canon_cmd, zed_cmd])

            set_continue += 1

        elif frame_flag_info['type'] == 'validation':
            print(magenta('[Validation SET] Total frame numbers to be used 120'))

            val_set_continue += 1
            canon_output_dir = os.path.join(__OUTPUT_DIR__, 'canon/validation/val_set{:02d}'.format(val_set_continue))
            zed_output_dir = os.path.join(__OUTPUT_DIR__, 'zed/validation/val_set{:02d}'.format(val_set_continue))

            for i in range(120):
                canon_cmd = [os.path.join(canon_frame_dir, 'canon{:06d}.png'.format(int(canon_starting_frame)+i)),
                             os.path.join(canon_output_dir, 'frame{:03d}.png'.format(i))]
                zed_cmd = [os.path.join(zed_frame_dir, 'zed{:06d}.png'.format(int(zed_starting_frame)+i)),
                             os.path.join(zed_output_dir, 'frame{:03d}.png'.format(i))]

                pool.map(copy_frames_to, [canon_cmd, zed_cmd])

        elif frame_flag_info['type'] == 'test':
            print(magenta('[Test SET] Total frame numbers to be used 120'))

            test_set_continue += 1
            canon_output_dir = os.path.join(__OUTPUT_DIR__, 'canon/test/test_set{:02d}'.format(test_set_continue))
            zed_output_dir = os.path.join(__OUTPUT_DIR__, 'zed/test/test_set{:02d}'.format(test_set_continue))

            for i in range(120):
                canon_cmd = [os.path.join(canon_frame_dir, 'canon{:06d}.png'.format(int(canon_starting_frame) + i)),
                             os.path.join(canon_output_dir, 'frame{:03d}.png'.format(i))]
                zed_cmd = [os.path.join(zed_frame_dir, 'zed{:06d}.png'.format(int(zed_starting_frame) + i)),
                           os.path.join(zed_output_dir, 'frame{:03d}.png'.format(i))]

                pool.map(copy_frames_to, [canon_cmd, zed_cmd])

        else:
            continue