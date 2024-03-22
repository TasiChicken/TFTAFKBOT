import win32gui
import win32con
import time

CLIENT_WINDOW = 'League of Legends'
GAME_WINDOW = 'League of Legends (TM) Client'


def hide_window_for_sec(window_title, minTime = 0):
    while minTime >= 0:
        time.sleep(0.02)
        minTime -= 0.02
        hwnd = win32gui.FindWindow(None, window_title)
        if hwnd:
            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)

def show_window(window_title):
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
        return

if __name__ == "__main__":
    show_window(CLIENT_WINDOW)
    show_window(GAME_WINDOW)