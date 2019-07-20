import os
import argparse
from shutil import move
from utils.print_utils import magenta, yellow, red



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, help="A date(in YYmmDD format) which you want to process.(example: 20190612)")
    parser.add_argument("--mode", type=str, help="Which dataset that you want to sort out. [IMG | VID]")
    parser.add_argument('--set_continue', default= 0, type=int, help='Continue to create the set from this number.')
    args = parser.parse_args()

    date= args.date
    mode = args.mode
    set_count = args.set_continue

    if mode != 'IMG' and mode !='VID':
        print(red('Please choose the mode between [ IMG | VID ]'))
        exit(-1)
    if mode == 'VID':
        __INPUT_DIR__ = './saved_data/VID/{}/'.format(date)
        __LOG_FILE__ = './saved_data/VID/{}/video_capture.log'.format(date)
        __OUTPUT_DIR__ = './saved_data/VID/{}/sorted'.format(date)
    else: # images
        __INPUT_DIR__ = './saved_data/IMG/{}/'.format(date)
        __OUTPUT_DIR__ = '../saved_data/IMG/{}/sorted/'.format(date)

    i = 0
    for files in os.listdir(__OUTPUT_DIR__):
        src_folder = os.path.join(__OUTPUT_DIR__, files)
        dst_folder = os.path.join(__OUTPUT_DIR__, 'set{:03d}'.format(set_count))
        move(src_folder, dst_folder)
        set_count +=1


    print('Done!')


