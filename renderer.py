from executor import ShouldRun, GetRenderFrameCount, SetPrecachedFrameCount, SetFPS
from performance import PerfObject
from PIL import Image
import threading
import decord
import time

# Render Thread
#
# This thread is used to read the frames from the mp4 file and to precache them for the converter.
# It's a wonder that we don't need any threadlocks. I would have expected it to crash with all the threads that write stuff but It's just working too well.

read_frames = None
precached_current_frames = 0
precached_finished_frames = 0
renderthreads_count = 0
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

    if read_frames[frame] is not None: # Rare case
        read_frames[frame].close()
        read_frames[frame] = None

    del perf

def GetFrameCount():
    return framecount

def SetVideo(file, threadcount):
    global video, fps, framecount, read_frames, precached_current_frames, precached_finished_frames, fps
    video = []
    for x in range(0, threadcount):
        # Each thread has it's own VideoReader.
        # We need this because the VideoReader can only be used by one thread at a time and to workaround this, each thread will have it's own.
        # We create them on the main thread since else they won't work.
        video.append(decord.VideoReader(file, decord.cpu(0), -1, -1, 4))
    framecount = len(video[0])
    read_frames = [None] * framecount
    SetFPS(1 / video[0].get_avg_fps())
    precached_current_frames = 0
    precached_finished_frames = 0

class renderThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global precached_current_frames, precached_finished_frames, renderthreads_count
        thread_id = renderthreads_count
        renderthreads_count += 1
        while ShouldRun():
            perf = PerfObject("Renderer")

            frame_count = precached_current_frames
            precached_current_frames += 1

            while GetPrecachedFrames() > (GetRenderFrameCount() + max_precache) and ShouldRun():
                time.sleep(1/50)

            if precached_current_frames > GetFrameCount():
                del perf
                break

            perf_readframe = PerfObject("Read Frame")
            current_frame = video[thread_id][frame_count] # A slow part...... TODO: Figure out why performance worsens with more threads.
            del perf_readframe

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