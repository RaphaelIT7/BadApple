from PIL import Image
import threading
import time
from performance import PerfObject
from renderer import GetFrame, RemoveFrame, GetFrameCount
from executor import ShouldRun, SetFrameCount, SetFinalFrameCount, GetFinalFrameCount

# Coverter Thread
#
# This thread is used to convert read frames to ASCII so that they are ready to be displayed.

final_frames = None
renderer_current_frame = 0
backlog_current_frames = 0
backlog_finished_frames = 0
def RemoveFinalFrame(frame):
    if frame < 0:
        return

    perf = PerfObject("Remove Final Frame")
    #print(f"Removed Final Frame {frame}")
    final_frames[frame] = None

def GetFinalFrame(frame):
    perf = PerfObject("GetFinalFrame")
    global renderer_current_frame, skipped_frames
    RemoveFinalFrame(renderer_current_frame-1)
    renderer_current_frame += frame

    for i in range(frame - 1): # BUG: Why is skipping frames so expensive? / Why does it cause laggs? NOTE: It seems to be causes by the threadLocks FIX: Removed the threadlocks.
        RemoveFinalFrame(renderer_current_frame)
        renderer_current_frame += 1
        skipped_frames += 1
    
    while backlog_finished_frames < renderer_current_frame and ShouldRun():
        time.sleep(0)

    SetFrameCount(renderer_current_frame)
    
    #print(f"Frame {renderer_current_frame}, {GetFinalFrameCount()}, {GetFrameCount()}")
    if renderer_current_frame >= GetFinalFrameCount():
        return None

    return final_frames[renderer_current_frame]

new_width = 1200 # Should be able to up to 1200. BUG: Why does this Influence the render threads performance :<

grey_chars = [
    '@', '#', '8', '&', 'B', '%', 'M', 'W', '*', 'o', 'a', 'h', 'k', 'b', 'd', 'p', 'q',
    'w', 'm', 'Z', 'O', '0', 'Q', 'L', 'C', 'J', 'U', 'Y', 'X', 'z', 'c', 'v', 'u', 'n',
    'x', 'r', 'j', 'f', 't', '/', '|', '(', ')', '1', '{', '}', '[', ']', '?', '-', '_',
    '+', '~', '<', '>', 'i', '!', 'l', 'I', ';', ':', ',', '"', '^', '`', '\'', '.', ' '
]

characters = []

# We calculate the gray scale here so that we don't need to do it later for each pixel.
for i in range(256):
    brightness = i
    index = int((brightness / 255) * (len(grey_chars) - 1))
    characters.append(grey_chars[index])

# image resize function
def resize_image(image):
    perf = PerfObject("Resize Image")
    width, height = image.size
    ratio = height / width / 2.5 # This needs to be adjusted for different Videos

    return image.resize((new_width, int(new_width * ratio)), Image.Resampling.NEAREST, None, 1)

# convert pixels to greyscale
def greyscaling(image):
    perf = PerfObject("Grey Scaling")
    return image.convert("L")

# convert pixel to greyscale as desired
def new_pixel_convertor(image):
    perf = PerfObject("Pixel To ASCII")
    return "".join([characters[pixel] for pixel in image.getdata()]) # This is the slowest part

class converterThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global final_frames
        final_frames = [None] * GetFrameCount()

        global backlog_current_frames, backlog_finished_frames
        while ShouldRun():
            perf = PerfObject("Converter")

            frame_count = backlog_current_frames
            backlog_current_frames += 1
            if backlog_current_frames > GetFrameCount():
                del perf
                break

            current_frame = GetFrame(frame_count)
            if current_frame is None:
                continue # No Frame? I don't care.

            perf2 = PerfObject("Read Image")
            current_frame = Image.fromarray(current_frame.asnumpy()) # .asnumpy is slow :<
            del perf2

            if not ShouldRun():
                break

            new_image_data = new_pixel_convertor(greyscaling(resize_image(current_frame)))
            pixel_count = len(new_image_data)
            ascii_image = "\n".join(new_image_data[i:(i+new_width)] for i in range(0, pixel_count, new_width))

            final_frames[frame_count] = ascii_image
            backlog_finished_frames += 1
            SetFinalFrameCount(backlog_finished_frames)
            #print(f"Final frame: {frame_count}")
    
            current_frame.close()
            RemoveFrame(frame_count)
            del perf