commands = """
import subprocess
import os
import signal

nullin = open(os.devnull, 'r')
nullout = open(os.devnull, 'w')

OMX_CMD = ['omxplayer', '--no-osd', '--no-keys', '--refresh']
OMX_LOOP_CMD = ['omxplayer', '--no-osd', '--no-keys', '--refresh', '--loop']

mycmd1 = OMX_CMD + ["1960s-family-vacation-keys.mp4"]
mycmd2 = " ".join(mycmd1)
"""

exec(commands)
print commands

print """
Try this:

#proc = Popen(mycmd1, stdin=nullin,stdout=nullout)
proc = subprocess.Popen(mycmd2, shell=True)
os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
"""
