should_run = True

def ShouldRun():
    return should_run

def Shutdown():
    global should_run
    should_run = False

frame_count = 0
def SetFrameCount(frame):
    global frame_count
    frame_count = frame

def GetRenderFrameCount():
    return frame_count

audioframe_count = 0
def SetAudioFrameCount(frame):
    global audioframe_count
    audioframe_count = frame

def GetAudioFrameCount():
    return audioframe_count

finalframe_count = 0
def SetFinalFrameCount(frame):
    global finalframe_count
    finalframe_count = frame

def GetFinalFrameCount():
    return finalframe_count

precachedframe_count = 0
def SetPrecachedFrameCount(frame):
    global precachedframe_count
    precachedframe_count = frame

def GetPrecachedFrameCount():
    return precachedframe_count

fps = 0
def SetFPS(newFps):
    global fps
    fps = newFps

def GetFPS():
    return fps

renderthreadcount = 0
def SetRenderThreadCount(count):
    global renderthreadcount
    renderthreadcount = count

def GetRenderThreadCount():
    return renderthreadcount

converterthreadcount = 0
def SetConverterThreadCount(count):
    global converterthreadcount
    converterthreadcount = count

def GetConverterThreadCount():
    return converterthreadcount

fontSize = 0
def SetFontSize(size):
    global fontSize
    fontSize = size

def GetFontSize():
    return fontSize