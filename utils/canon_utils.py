from time import sleep, clock
from subprocess import check_output, call, check_call
import signal, os, subprocess

__LOCAL_PC_PATH__ = '/home/sokim/D5_images'
DEBUG = False

# Kill the gphoto process that starts
# whenever we turn on the camera or
# reboot the raspberry pi

def killGphoto2Process():
    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate()

    # Search for the process we want to kill
    for line in out.splitlines():
        if b'gvfsd-gphoto2' in line:
            # Kill that process!
            pid = int(line.split(None,1)[0])
            os.kill(pid, signal.SIGKILL)

def press_shutter_button():
    if DEBUG: print('[Canon] press_camera_button'.ljust(20), clock())
    r = check_output(['gphoto2', '--capture-image'])
    if DEBUG: print(r.strip().decode('utf8'))


def capture_image_and_download(directory, count=0):
    if DEBUG: print('[Canon] capture and download to'.ljust(20), clock())
    r = check_output(['gphoto2', '--capture-image-and-download', '--filename', os.path.join(directory, '%f.%C')])
    #r = check_output(['gphoto2', '--capture-image-and-download', '--filename', os.path.join('./tempD5', '%f.%C')])
    #msg = r.strip().decode('utf8')
    # img_name ='d5_IMG_{}.%C'.format(count)
    if DEBUG: print(r.strip().decode('utf8'))

    return r.strip().decode('utf8')

def take_video_and_download(directory, time=12):
    '''
        Remote control of the taking videos from D5 mark IV
    :param directory: directiory of the file to be stored. (Must be created before calling)
    :param count: The number of movies taken
    :param time: The period of video in seconds
    :return:
    '''
    if DEBUG: print('[Canon] take video and download to'.ljust(20), clock())
    filespec = os.path.join(directory, "%f.%C")
    cmdline = ["gphoto2",
               "--set-config", "viewfinder=1",
               "--set-config", "capturetarget='Memory card'",
               "--set-config", "movierecordtarget=Card",
               "--wait-event", f"{time:.0f}s",
               "--set-config", "movierecordtarget=None",
               "--wait-event-and-download", "2s",
               "--filename", f"{filespec}"]
    if DEBUG: print(cmdline)
    r = check_output(cmdline)
    if DEBUG: print(r.decode('utf8'))

    return r.strip().decode('utf8')


def check_camera_summary():
    if DEBUG: print('[Canon] Camera summary'.ljust(20), clock())
    r = check_output(['gphoto2', '--summary'])
    if DEBUG: print(r.strip())
