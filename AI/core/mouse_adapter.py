from AI.core import mouse_win


def get_adapter(name="win32"):
    name = (name or "").lower()
    if name in ("win32", "windows", "ms"):
        return mouse_win.get_win32_adapter()
    raise ValueError(f"Unknown mouse adapter backend: {name}")
