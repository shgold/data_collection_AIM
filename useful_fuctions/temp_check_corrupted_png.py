import os
import cv2
from utils.print_utils import yellow, red

__BASE_DIR__ = '/media/dc2019/My Book/VID/VQM_data'
__TEST_DIR__ = os.path.join(__BASE_DIR__, 'zed/test')
__VALID_DIR__ = os.path.join(__BASE_DIR__, 'zed/validation')

sets = os.listdir(__TEST_DIR__)

for set in sets:
    set_dir = os.path.join(__TEST_DIR__, set)
    print(yellow(set_dir))
    frames = os.listdir(set_dir)
    for frame in frames:
        print(os.path.join(set_dir, frame))
        try:
            img = cv2.imread(os.path.join(set_dir, frame))
        except:
            print(red(os.path.join(set_dir, frame)))

print('Done!')