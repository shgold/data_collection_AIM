import os
import numpy as np
import cv2
import time



__BASE_PATH__ = '/media/dc2019/My Book/SORTED/Compressed/ZED'
__PATH_TO_CONFIDENCE_FOLDER__ = os.path.join(__BASE_PATH__, 'confidence')
__PATH_TO_DEPTH_LEFT_FOLDER__ = os.path.join(__BASE_PATH__, 'depth/left')


def compute_depth_density(depth_map):
    num_d_pixel = np.count_nonzero(depth_map)
    density = num_d_pixel / (depth_map.size)
    return density

def compute_depth_range(depth_map):
    depth_vals = np.unique(depth_img)
    depth_range = depth_vals[-1] - depth_vals[1]
    return depth_range

def compute_average_depth(depth_map):
    depth_avg = depth_map[np.nonzero(depth_map)].mean()
    return depth_avg


def compute_confidence_distribution(confidence_map):
    conf_num_pixel, conf_bins = np.histogram(confidence_map / 255 * 100, bins=range(0, 101, 10))
    conf_density = conf_num_pixel / confidence_map.size
    return conf_density


if __name__ == '__main__':
    __depth_files__ = [os.path.join(__PATH_TO_DEPTH_LEFT_FOLDER__, 'ZED_depth_left_{:06d}.png'.format(i)) for i in range(8384)]
    __confidence_files__ = [os.path.join(__PATH_TO_CONFIDENCE_FOLDER__, 'ZED_confidence_map_{:06d}.png'.format(i)) for i in range( 8384)]

    depth_density = np.zeros(8384)
    depth_range = np.zeros(8384)
    depth_average = np.zeros(8384)
    confidence_density = np.zeros((8384, 10))
    scene_num = 0
    str_time = time.time()
    for depth_img_path, confidence_map_path in zip(__depth_files__[scene_num:], __confidence_files__[scene_num:]):
        elaspe = time.time()-str_time
        print('[{:.3f}] currently scene {}'.format(elaspe, scene_num))

        depth_img = cv2.imread(depth_img_path,cv2.IMREAD_UNCHANGED)
        confi_map = cv2.imread(confidence_map_path, cv2.IMREAD_ANYDEPTH)
        depth_density[scene_num] = compute_depth_density(depth_img)
        depth_range[scene_num] = compute_depth_range(depth_img)
        depth_average[scene_num] = compute_average_depth(depth_img)
        confidence_density[scene_num] = compute_confidence_distribution(confi_map)

        scene_num += 1

    np.save(os.path.join(__BASE_PATH__, 'depth_density.npy'), depth_density)
    np.save(os.path.join(__BASE_PATH__, 'depth_range.npy'), depth_range)
    np.save(os.path.join(__BASE_PATH__, 'depth_average.npy'), depth_average)
    np.save(os.path.join(__BASE_PATH__, 'confidence_density.npy'), confidence_density)

    print('Done!')