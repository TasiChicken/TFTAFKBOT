import win32gui
import win32con
from time import sleep
import subprocess
import os
import psutil
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume

RIOT_PATH = r'C:\Riot Games\Riot Client\RiotClientServices.exe'
CLIENT_WINDOW = 'League of Legends'
CLIENT_EXE = 'LeagueClient.exe'
GAME_WINDOW = 'League of Legends (TM) Client'
GAME_EXE = 'League of Legends.exe'
RENDER_EXE = 'LeagueClientUxRender.exe'

def killTask(exe):
    os.system(f'taskkill /F /IM "{exe}"')

def lanuchClient():
    killTask(CLIENT_EXE)
    killTask(GAME_EXE)

    # Open League of Legends client
    print('lauching client')
    subprocess.Popen(f'"{RIOT_PATH}" --launch-product=league_of_legends --launch-patchline=live', shell=True)
    print('Waiting 30 sec for client lanuched completely')
    hide_window_for_sec(CLIENT_WINDOW, 30)

def getPortAndToken():
    data = None

    # Get data from client
    for process in psutil.process_iter():
        if process.name().removesuffix(".exe") == "LeagueClientUx":
            data = process.cmdline()
            break
        
    # If client was not found
    if data is None:
        raise WindowsError('lol client are not lanuched')
    
    # Extract port and token from data
    for param in data:
        info = param.split("=")
        if info[0] == "--app-port":
            port = info[1]
        if info[0] == "--remoting-auth-token":
            token = info[1]
    return (port, token)

def hide_window_for_sec(window_title, minTime = 0):
    while minTime >= 0:
        sleep(0.02)
        minTime -= 0.02
        hwnd = win32gui.FindWindow(None, window_title)
        if hwnd:
            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)

def show_window(window_title):
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
        return

def mute_application(process_name, muted = 1, persist = True):
    while True:
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            volume_interface = session._ctl.QueryInterface(ISimpleAudioVolume)
            if session.Process and session.Process.name() == process_name:
                volume_interface.SetMute(muted, None)  # 1 for mute, 0 for unmute
                return
        if not persist:
            return
        sleep(1)
        
def show():
    show_window(CLIENT_WINDOW)
    show_window(GAME_WINDOW)
    mute_application(RENDER_EXE, 0, False)
    mute_application(GAME_EXE, 0, False)

if __name__ == "__main__":
    show()