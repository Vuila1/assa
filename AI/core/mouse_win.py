import ctypes
from ctypes import wintypes

# Win32 constants
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_ABSOLUTE = 0x8000

# Types
ULONG = ctypes.c_ulong
LONG = ctypes.c_long
DWORD = ctypes.c_uint32

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", LONG),
        ("dy", LONG),
        ("mouseData", DWORD),
        ("dwFlags", DWORD),
        ("time", DWORD),
        ("dwExtraInfo", ctypes.POINTER(ULONG)),
    ]

class INPUT_union(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT)]

class INPUT(ctypes.Structure):
    _fields_ = [("type", DWORD), ("union", INPUT_union)]

SendInput = ctypes.windll.user32.SendInput

class Win32MouseAdapter:
    """Adapter that uses SendInput for mouse actions."""

    def __init__(self):
        self._si = SendInput

    def _send_input(self, dx, dy, flags, data=0):
        mi = MOUSEINPUT()
        mi.dx = dx
        mi.dy = dy
        mi.mouseData = data
        mi.dwFlags = flags
        mi.time = 0
        mi.dwExtraInfo = ctypes.cast(ctypes.pointer(ULONG(0)), ctypes.POINTER(ULONG))

        inp = INPUT()
        inp.type = 0  # INPUT_MOUSE
        inp.union.mi = mi

        res = self._si(1, ctypes.byref(inp), ctypes.sizeof(inp))
        if res == 0:
            raise ctypes.WinError()

    def move_relative(self, dx, dy):
        """Move mouse by relative amounts using SendInput MOUSEEVENTF_MOVE."""
        # Send relative movement
        self._send_input(int(dx), int(dy), MOUSEEVENTF_MOVE)

    def left_down(self):
        self._send_input(0, 0, MOUSEEVENTF_LEFTDOWN)

    def left_up(self):
        self._send_input(0, 0, MOUSEEVENTF_LEFTUP)


# Provide simple factory class name alias
def get_win32_adapter():
    return Win32MouseAdapter()
