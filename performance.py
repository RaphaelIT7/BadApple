import dearpygui.dearpygui as dpg
from executor import ShouldRun, GetPrecachedFrameCount, GetFinalFrameCount, GetFPS, GetConverterThreadCount
import threading
import time

# Performance Profiling
# 
# How it works:
#	We have a class named TimeObject.
#	It saves the Time it got created and when it gets removed.
#	It gets removed when it goes out of scope and is not use anywhere else in the whole code.
#	Then we add it into the code_timing map, and then we only need to print it.
#
# Example usage:
# perf = TimeObject("Example")
# NOTE: Never use the perf variable and don't use it global or save it anywhere else
# BUG: Inside for or while loops, use del to delete the Object! or else the performance report might bug out!

lock = threading.Lock() # I want to get rid of this.
code_timing = {}
active_scope = {}
class PerfObject:
    def __init__(self, category):
        self.create_time = time.perf_counter()
        thread = threading.currentThread()
        if thread not in active_scope:
            active_scope[thread] = []

        active_scope[thread].append(category)
        self.categories = active_scope[thread]

    def __del__(self):
        categories = self.categories

        elapsed_time = time.perf_counter() - self.create_time
        current_dict = code_timing

        for category in categories[:-1]:
            current_dict = current_dict.setdefault(category, {'time': 0.0, 'count': 1, 'children': {}})
            current_dict = current_dict['children']

        last_category = categories[-1]

        with lock:
            last_category_data = current_dict.setdefault(last_category, {'time': 0.0, 'count': 1, 'children': {}})
            last_category_data['time'] += elapsed_time
            last_category_data['count'] += 1

        if categories:
            categories.pop()

def format_timing_string(data, indent=0):
    result = ""
    for category, values in data.items():
        time_ms = (values['time'] / values['count']) * 1000

        bars = '| ' * indent if indent > 0 else ''
        result += f"{bars}{category} ({time_ms:.3f} ms)\n"

        if values['children']:
            result += format_timing_string(values['children'], indent + 1)
    return result


def get_time(category):
    cat = code_timing.get(category, {})
    time = cat.get("time", -1)
    if time == -1:
        return 0
    
    count = cat.get("count", -1)
    if count == -1:
        return 0

    return time / count

profilerText = ""
def getProfilerText():
    return profilerText

class performanceThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.frame = 0
        self.fps = 1 / 60 # Cap it at 60 until it gets set
        self.ft = 0
        self.maintime = 0
        self.convertime = 0
        self.last_frame = 0
        self.skipped_frames = 0
        self.frametime = 0
        self.stats_txt = None
        self.player = None
    def update(self, frametime, frame, last_frame, skipped_frames, fps, stats_txt, player):
        if frametime is not None:
            self.frametime = frametime

        if frame is not None:
            self.frame = frame
            # print("Got Stats", frame)

        if last_frame is not None:
            self.last_frame = last_frame

        if skipped_frames is not None:
            self.skipped_frames = skipped_frames

        if fps is not None:
            self.fps = fps

        if stats_txt is not None:
            self.stats_txt = stats_txt

        if player is not None:
            self.player = player
    def run(self):
        print ("Starting Stats Thread")
        global profilerText
        while ShouldRun():
            stats = "--- Stats ---\n"
            stats += f"Current Frame: {self.frame}\n"
            stats += f"Last Frame: {self.last_frame}\n"
            if self.player is not None:
                stats += f"Audio Frame: {round(self.player.get_pts() / self.fps)}\n"
            stats += f"Skipped Frames: {self.skipped_frames}\n"
            stats += f"Precached Frames: {GetPrecachedFrameCount()}\n"
            stats += f"Final Frames: {GetFinalFrameCount()}\n"

            stats += "\n"
            if get_time("Main") != 0:
                self.maintime = round(1 / get_time("Main"))

            if get_time("Converter") != 0:
                self.convertime = round(1 / (get_time("Converter") / GetConverterThreadCount()))

            if self.frametime != 0:
                self.ft = round(1 / self.frametime)

            stats += f"FPS: {self.maintime}\n"
            stats += f"Required FPS: {1 / GetFPS()}\n"
            stats += f"Converter FPS: {self.convertime}\n" # If this is below Required FPS, we may start to fall behind.

            stats += "\n\n"
            stats += format_timing_string(code_timing)

            profilerText = stats
            time.sleep(self.fps)