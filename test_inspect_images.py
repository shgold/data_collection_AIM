import time
import os
import glob
import utils.log_utils as logutils

import matplotlib.pyplot as plt


__D5_PATH__ = './saved_data/IMG/{}/D5'.format(time.strftime('%Y%m%d'))
__ZED_PATH__ = "./saved_data/IMG/{}/ZED".format(time.strftime('%Y%m%d'))
__P20_PATH__ = "./saved_data/IMG/{}/P20/Camera".format(time.strftime('%Y%m%d'))

input_dir = './saved_data/IMG/{}/'.format(time.strftime('%Y%m%d'))
log_dir = './saved_data/IMG/{}/image_capture.log'.format(time.strftime('%Y%m%d'))
output_dir = './saved_data/IMG/{}/compare_images'.format(time.strftime('%Y%m%d'))

zed_path = sorted(os.listdir(__ZED_PATH__))
d5_path = sorted(os.listdir(__D5_PATH__))[1::2] # choose only jpg
p20_path = sorted(os.listdir(__P20_PATH__))


def show_images(d5, p20, zed):
    plt.subplot(131)
    plt.imshow(d5)
    plt.title('D5')
    plt.axis('off')

    plt.subplot(132)
    plt.imshow(p20)
    plt.title('P20')
    plt.axis('off')

    plt.subplot(133)
    plt.imshow(zed)
    plt.title('ZED')
    plt.axis('off')

    plt.show()
    plt.pause(2)



if __name__ == '__main__':

    # list is in [D5, P20, ZED] order
    list_vid_dir = logutils.read_log_file(log_dir, input_dir, is_video=False)

    # Create output_folder
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i, sets in enumerate(list_vid_dir):
        zed_img = plt.imread(sets[2])
        p20_img = plt.imread(sets[1])
        d5_img = plt.imread(sets[0])
        plt.ion()
        show_images(d5_img, p20_img, zed_img)
        plt.savefig(os.path.join(output_dir,'set_{}.png'.format(i)))


    print('Done!')
