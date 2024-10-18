import time
import threading

from ffpyplayer.player import MediaPlayer

import os
import yt_dlp
import ffmpeg
import dearpygui.dearpygui as dpg
import yt_dlp.downloader
from performance import PerfObject, performanceThread
from renderer import renderThread, SetVideo, GetFrameCount
from converter import converterThread, GetFinalFrame
from executor import Shutdown, GetRenderFrameCount, SetAudioFrameCount, ShouldRun, GetFPS

frametime = 1
main_thread = threading.current_thread()
threads = []

def set_text(text):
    perf = PerfObject("Set Text")
    dpg.set_value(image_txt, text)
    del perf

# Main Fucntion u stupid banana
def main(count, frame):
    perf = PerfObject("Frame")

    if frame <= 0:
        return

    newText = GetFinalFrame(1)
    if (newText is not None):
        set_text(newText)


file = "Touhou - Bad Apple.mp4"

def shutdown():
    print("Shutdown")
    global running
    running = False
    Shutdown()
    #player.close_player()
    dpg.destroy_context()

def player():
    try:
        global frametime, player, int_count, last_frame, running, sleep, skipped_frames, perfThread, fps, file

        global image_txt, stats_txt

        with dpg.window(tag="Player", label="sex"):
            with dpg.group(horizontal=True):
                image_txt = dpg.add_text("Segsy")
                dpg.bind_item_font(image_txt, small_font)
                with dpg.group(horizontal=False):
                    stats_txt = dpg.add_text("Stats")
                    dpg.bind_item_font(stats_txt, normal_font)

        dpg.set_primary_window("Player", True)
        dpg.hide_item("Primary")

        yt_opts = {
            'verbose': True,
            # 'outtmpl': '../Video/Cache',
        }

        if file.startswith("https://"):
            with yt_dlp.YoutubeDL(yt_opts) as ydl:
                try:
                    ydl.download(file)
                except:
                    pass

        if not file.endswith(".mp4"):
            dot = file.rfind('.')
            new_file = ""
            if dot != -1:
                new_file = file[:dot] + '.mp4'

            if os.path.exists(file):
                ffmpeg.input(file).output(new_file).run()
                os.remove(file)
                file = new_file
            else:
                file = new_file

        SetVideo(file, 1)

        options = {"sync" : "audio", "framedrop" : True, "volume" : 0.1, "vn" : True, "sn" : True}
        player = MediaPlayer(file, ff_opts = options)

        fps = GetFPS()
        total_frames = GetFrameCount()

        int_count = 0
        last_frame = -1
        skipped_frames = 0
        running = True

        perfThread = performanceThread()
        threads.append(perfThread)
        threads.append(renderThread()) # SetVideo second arg is the number of threads you will use. BUG: More = Worse performance? Idk why
        threads.append(converterThread())
        threads.append(converterThread())
        threads.append(converterThread())
        threads.append(converterThread())
        threads.append(converterThread())
        threads.append(converterThread())

        for thread in threads:
            thread.start()

        while (int_count <= total_frames) and ShouldRun():
            perf = PerfObject("Main")

            t0 = time.perf_counter()
            main(int_count, int_count - last_frame)
            t1 = time.perf_counter()

            frametime = (t1 - t0)
            #if (frametime > fps):
            #    print("LAG!")

            sleep = (fps - (frametime * 2) - 0.005) / 4 # Running four times per frame should allow us to play frames that would otherwise be skipped

            if sleep > 0:
                perf2 = PerfObject("Sleep")
                time.sleep(sleep)
                del perf2

            perf_postupdate = PerfObject("Post Frame")
            last_frame = GetRenderFrameCount()
            int_count = round(player.get_pts() / fps) # player.get_pts() is expensive. Call it a second time and there goes your performance.
            SetAudioFrameCount(int_count)
            perfThread.update(frametime, int_count, last_frame, skipped_frames, fps, stats_txt, player)
            del perf_postupdate
            del perf

        shutdown()
        
    except KeyboardInterrupt:
        shutdown()

# Textscreen
dpg.create_context()

with dpg.font_registry():
    small_font = dpg.add_font("ProggyClean.ttf", 2.5)
    normal_font = dpg.add_font("ProggyClean.ttf", 13)

with dpg.window(tag="Primary", label="sex"):
    button = dpg.add_button(label="Run", callback=player)
    dpg.bind_item_font(button, normal_font)

dpg.create_viewport(resizable=True)
dpg.setup_dearpygui()
dpg.set_primary_window("Primary", True)
dpg.show_viewport()
try: # Handle crashes. If we want to close it, it should close and not crash.
    dpg.start_dearpygui()
except:
    pass

shutdown()