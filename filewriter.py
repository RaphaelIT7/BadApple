from executor import ShouldRun
from performance import PerfObject
from renderer import GetFrameCount
from converter import SetFinalFrame, SetFinalFrameCount
import threading
import time
import os

# File Thread
#
# This thread is used to write each file to disk.

hasWriteThreads = False
def HasWriteThreads():
    return hasWriteThreads

framesToSave = {}
def AddFrameToSave(frameNumber, text):
    if not HasWriteThreads():
        return

    global framesToSave
    framesToSave[frameNumber] = text

def ReadFrameFromSave(frameNumber):
    if not os.path.isfile("lastRender/" + str(frameNumber) + ".txt"):
        return None

    return open("lastRender/" + str(frameNumber) + ".txt", "r").read()

fileLock = threading.Lock()
filethreads_count = 0
class fileWriteThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        global hasWriteThreads
        hasWriteThreads = True

    def run(self):
        global filethreads_count
        global framesToSave
        thread_id = filethreads_count
        filethreads_count += 1
        while (ShouldRun() or len(framesToSave) != 0): # Only stop if there is nothing left
            perf = PerfObject("File")

            while len(framesToSave) == 0 and ShouldRun():
                time.sleep(1/50)

            if not ShouldRun() and len(framesToSave) == 0:
                del perf
                break

            perf_readframe = PerfObject("Write Frame to Disk")

            frameNumber = -1
            frameText = None

            with fileLock:
                for frame in list(framesToSave.keys()):
                    frameNumber = frame
                    frameText = framesToSave[frame]
                    del framesToSave[frame]
                    break

            open("lastRender/" + str(frameNumber) + ".txt", "w").write(frameText)

            del perf_readframe
            del perf

class fileReadThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        perf = PerfObject("File")
        global filethreads_count
        global framesToSave
        thread_id = filethreads_count
        filethreads_count += 1

        if thread_id > 1: # We only need 1 thread
            del perf
            return
        
        for frame in range(0, GetFrameCount()):
            perf_readframe = PerfObject("Read Frame from Disk")

            text = ReadFrameFromSave(frame)
            if text is not None:
                SetFinalFrame(frame, text)
                SetFinalFrameCount(frame)

            del perf_readframe

            #print("Loading " + str(frame))

        del perf