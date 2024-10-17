from executor import ShouldRun, GetRenderFrameCount, SetPrecachedFrameCount
from performance import PerfObject
from PIL import Image
import threading
import time

# Render Thread
#
# This thread is used to read the frames from the mp4 file and to precache them for the converter.

threadLock = threading.Lock()

read_frames = None
precached_current_frames = 0
precached_finished_frames = 0
max_precache = 500 # Higher Number = Higher Memory Usage
def GetPrecachedFrames():
    return precached_current_frames

def GetFrame(frame):
    perf = PerfObject("GetFrame")
    while read_frames[frame] is None and ShouldRun():
        time.sleep(0)

    return read_frames[frame]

def RemoveFrame(frame):
    perf = PerfObject("Remove Final Frame")
    #threadLock.acquire()
    read_frames[frame].close()
    read_frames[frame] = None
    #threadLock.release()
    del perf

def GetFrameCount():
    return framecount

def SetVideo(vid):
    global video, framecount, read_frames, precached_current_frames, precached_finished_frames
    video = vid
    framecount = len(vid)
    read_frames = [None] * framecount
    precached_current_frames = 0
    precached_finished_frames = 0

class renderThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global precached_current_frames, precached_finished_frames
        while ShouldRun():
            perf = PerfObject("Renderer")

            frame_count = precached_current_frames
            precached_current_frames += 1

            while GetPrecachedFrames() > (GetRenderFrameCount() + max_precache) and ShouldRun():
                time.sleep(1/50)

            if precached_current_frames > GetFrameCount():
                del perf
                break

            threadLock.acquire()

            current_frame = video[frame_count] # The slowest part..... We need the locks because else decord will crash

            threadLock.release()

            if current_frame is not None:
                perf2 = PerfObject("Read Image")
                img = Image.fromarray(current_frame.asnumpy())

                perf3 = PerfObject("Add Image")
                read_frames[frame_count] = img
                precached_finished_frames += 1
                SetPrecachedFrameCount(precached_finished_frames)
                #print(f"Read frame: {frame_count}")

                del perf3
                del perf2

            del perf