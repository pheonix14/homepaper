import ctypes
import ctypes.wintypes as wintypes

user32 = ctypes.windll.user32

# Constants
SMTO_NORMAL = 0x0000
MSG_SPAWN_WORKERW = 0x052C

def spawn_workerw():
    """
    Sends a message to Progman to spawn a WorkerW window behind the desktop icons.
    """
    progman = user32.FindWindowW("Progman", None)
    if not progman:
        print("Could not find Progman.")
        return False
    
    # Send 0x052C message to Progman
    result = ctypes.c_long()
    user32.SendMessageTimeoutW(
        progman,
        MSG_SPAWN_WORKERW,
        0,
        0,
        SMTO_NORMAL,
        1000,
        ctypes.byref(result)
    )
    return True

def get_workerw():
    """
    Finds the WorkerW window that is the sibling of the window containing the desktop icons.
    """
    workerw_hwnd = [0]

    # Callback for EnumWindows
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)

    def enum_windows_callback(hwnd, lParam):
        # We are looking for the window class "SHELLDLL_DefView"
        p = user32.FindWindowExW(hwnd, 0, "SHELLDLL_DefView", None)
        if p != 0:
            # We found the DefView, now we get its next sibling, which is the WorkerW we want.
            workerw_hwnd[0] = user32.FindWindowExW(0, hwnd, "WorkerW", None)
        return True

    user32.EnumWindows(WNDENUMPROC(enum_windows_callback), 0)
    return workerw_hwnd[0]

def set_wallpaper_window(hwnd):
    """
    Sets the given window handle as the child of the WorkerW window.
    """
    if not spawn_workerw():
        return False
        
    workerw = get_workerw()
    if not workerw:
        print("Could not find WorkerW. Spawning might have failed.")
        return False
        
    # Set the parent
    user32.SetParent(hwnd, workerw)
    return True
