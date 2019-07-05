import os
import subprocess
import signal
'''
    This script kills gvfsd process that blocks the remote control of DSLR from the computer.
    Recommended to run this script when connecting DSLR to the computer. 
    
    HOW TO USE:
    python3 temp_kill_gvfs.py 
'''


def killGphoto2Process():
    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate()

    # Search for the process we want to kill
    for line in out.splitlines():
        if b'gvfsd-gphoto2' in line:
            # Kill that process!
            pid = int(line.split(None,1)[0])
            os.kill(pid, signal.SIGKILL)

if __name__=='__main__':
    killGphoto2Process()
    print('killed')

