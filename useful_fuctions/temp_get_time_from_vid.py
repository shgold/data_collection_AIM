import glob
import os
import numpy as np

time_logger = []
for file in glob.glob("/media/dc2019/My Book/VID/00_RAW/*/*/*.mp4"):
    fname = os.path.basename(file)
    _time = fname.split('.mp4')[0].split('_')[-1]
    time_logger.append(_time)


np.savetxt(os.path.join('/media/dc2019/My Book/VID/00_RAW/', 'time_vid.txt'), np.asarray(time_logger, dtype=int), delimiter=' ')