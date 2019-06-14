import pyzed.sl as sl
import utils.zed_utils as zutils
import utils.log_utils as logutils
import time
import os
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_path", help="folder to save the captured zed image or recorded zed video")
    parser.add_argument("--log_file", help="path to save the log file")
    parser.add_argument("--adjust_time", default= 5, help='A period of time(in seconds) to adjust on the lighting environment when opened.')
    parser.add_argument("--vid_time", default =None, help="A period of time(in seconds) of video recording. "
                                                          "When not specified(default=None), it will capture the zed image.")
    args = parser.parse_args()

    if args.vid_time is None: # Capture images
        # Set parameters
        __ZED_IMG_PATH__ = args.out_path
        __IMG_LOGGING_FILE__ = args.log_file
        __ADJUST_TIME__ = int(args.adjust_time)

        # Create logger
        img_logger = logutils.create_logger(__IMG_LOGGING_FILE__)

        # Configure zed camera and open it
        zed, runtime = zutils.configure_zed_camera()

        # Time to adjust ZED camera to the lights
        time.sleep(__ADJUST_TIME__)

        if zed.grab(runtime) == sl.ERROR_CODE.SUCCESS:
            starting_time = time.time()
            print('{} starting zed'.format(starting_time))

            # Set the output directory and the filename
            img_folder = zed.get_timestamp(sl.TIME_REFERENCE.TIME_REFERENCE_IMAGE)
            directory = os.path.join(__ZED_IMG_PATH__, str(img_folder)[:10] + '/')
            if not os.path.exists(directory):
                os.makedirs(directory)
            filename = directory + 'zed'

            # Save the images and relevant information
            zutils.save_depth(zed, filename)
            zutils.save_rgb_image(zed, filename)
            zutils.save_unrectified_rgb_image(zed, filename)
            zutils.save_other_image(zed, filename)
            zutils.save_parameters(zed, filename)

            # Saving done!
            time_period = time.time() - starting_time
            print('[{:.3f}s] exiting ZED'.format(time_period))
            img_logger.info('IMAGE:ZED:{}'.format(str(img_folder)[:10]))

        # Close zed
        zed.disable_spatial_mapping()
        zed.disable_tracking()
        zed.close()

    else: # Record videos
        # Set parameters
        __ZED_VID_PATH__ = args.out_path
        __VID_LOGGING_FILE__ = args.log_file
        __VID_TIME__ = int(args.vid_time)
        __ADJUST_TIME__ = int(args.adjust_time)

        # Create logger
        vid_logger = logutils.create_logger(__VID_LOGGING_FILE__)

        # Configure zed camera and open it
        zed, runtime = zutils.configure_zed_camera(img_capture=False)

        # Time to adjust ZED camera to the lights
        time.sleep(__ADJUST_TIME__)

        # Enable video recording
        zed_vid_name = 'ZED_VID_{}.svo'.format(time.strftime('%Y%m%d%H%M%S'))
        err = zed.enable_recording(os.path.join(__ZED_VID_PATH__, zed_vid_name),
                                   sl.SVO_COMPRESSION_MODE.SVO_COMPRESSION_MODE_LOSSLESS)

        if err != sl.ERROR_CODE.SUCCESS:
            print(repr(err))
            exit(-1)

        starting_time = time.time()
        print('{} starting zed'.format(starting_time))

        # Start recording videos
        while time.time() - starting_time <= __VID_TIME__:      # for frame_counts in range(30*__VID_TIME__+1):
            if zed.grab(runtime) == sl.ERROR_CODE.SUCCESS:
                #print('Current frame fps:', zed.get_current_fps())
                zed.record()

        # Stop recording
        zed.disable_recording()
        time_period = time.time() - starting_time
        print('[{:.3f}s] exiting ZED'.format(time_period))
        vid_logger.info('VIDEO:ZED:{}'.format(zed_vid_name))

        # Close zed
        zed.close()