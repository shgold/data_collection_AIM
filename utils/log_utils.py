import logging
import time,datetime
import os

def create_logger(log_dir):

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler(log_dir)
    fh.setLevel(logging.INFO)
    formatter=logging.Formatter('%(asctime)s:%(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger



def read_log_file(log_file, file_dir, is_video=False):
    is_filename = False
    d5_dir = None
    p20_dir = None
    zed_dir = None

    list_sets =[]

    with open(log_file, 'r') as log_f:
        for line in log_f:
            last_entry = line.split(':')[-1]
            if len(last_entry) == 16:
                is_filename = True
                count = 0
                continue

            if is_video:
                if is_filename:
                    if 'VIDEO:D5' in line:
                        d5_dir = os.path.join(file_dir, 'D5/{}'.format(last_entry[:-1]))
                    if 'VIDEO:P20' in line:
                        p20_dir = os.path.join(file_dir, 'P20/{}'.format(last_entry[:-1]))
                    if 'VIDEO:ZED' in line:
                        zed_dir = os.path.join(file_dir, 'ZED/{}'.format(last_entry[:-1]))
                    count += 1
                    if count == 3:
                        if all([d5_dir, p20_dir, zed_dir]):
                            video_sets = [d5_dir, p20_dir, zed_dir]
                            list_sets.append(video_sets)
                        is_filename = False

            else: # for images
                if is_filename:
                    if 'IMAGE:D5' in line:
                        d5_dir=[]
                        d5_dir.append(os.path.join(file_dir, 'D5/{}.JPG'.format(last_entry[:-1])))
                        d5_dir.append(os.path.join(file_dir, 'D5/{}.CR2'.format(last_entry[:-1])))

                    if 'IMAGE:P20' in line:
                        p20_dir =[]
                        p20_jpg_file_name = line.split(':')[-1][:-1]
                        p20_raw_file_name = line.split(':')[-2]
                        p20_dir.append(os.path.join(file_dir, 'P20/{}'.format(p20_jpg_file_name)))
                        p20_dir.append(os.path.join(file_dir, 'P20/{}'.format(p20_raw_file_name)))

                    if 'IMAGE:ZED' in line:
                        zed_dir = os.path.join(file_dir, 'ZED/{}'.format(last_entry[:-1]))
                    count += 1
                    if count == 3:
                        if all([d5_dir, p20_dir, zed_dir]):
                            video_sets = [d5_dir, p20_dir, zed_dir]
                            list_sets.append(video_sets)
                        is_filename = False

    return list_sets


def check_p20_file_directory(p20_file_name, file_dir, is_video=False):

    if is_video:
        p20_dir = os.path.join(file_dir, 'P20/Camera/{}'.format(p20_file_name))

        if os.path.exists(p20_dir):
            return p20_dir
        else:
            # Find a file that has closest time name
            current_file_time = datetime.datetime.strptime(p20_file_name, 'VID_%Y%m%d_%H%M%S.mp4')
            seconds_diff = [-2, -1, 1, 2]
            for diff in seconds_diff:
                new_file_time = current_file_time + datetime.timedelta(seconds = diff)
                new_p20_name = 'VID_{}'.format(new_file_time.strftime('%Y%m%d_%H%M%S'))
                new_p20_dir = os.path.join(file_dir, 'P20/Camera/{}.mp4'.format(new_p20_name))

                if os.path.exists(new_p20_dir):
                    p20_dir = new_p20_dir
                    return p20_dir

            return None

    else:
        p20_dir = os.path.join(file_dir, 'P20/Camera/{}.jpg'.format(p20_file_name))

        if os.path.exists(p20_dir):
            return p20_dir
        else:
            # Find a file that has closest time name
            current_file_time = datetime.datetime.strptime(p20_file_name, 'IMG_%Y%m%d_%H%M%S')
            seconds_diff = [-2, -1, 1, 2]
            for diff in seconds_diff:
                new_file_time = current_file_time + datetime.timedelta(seconds = diff)
                new_p20_name = 'IMG_{}'.format(new_file_time.strftime('%Y%m%d_%H%M%S'))
                new_p20_dir = os.path.join(file_dir, 'P20/Camera/{}.jpg'.format(new_p20_name))

                if os.path.exists(new_p20_dir):
                    p20_dir = new_p20_dir
                    return p20_dir

            return None