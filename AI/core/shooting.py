import threading
import time

from AI.core.mouse_adapter import get_adapter


class ShootingThread(threading.Thread):
    def __init__(self, config=None):
        super().__init__(daemon=True)
        self.config = config or {}
        self.adapter = get_adapter(self.config.get("backend", "win32"))
        self.running = threading.Event()
        self.rate = self.config.get("fire_rate", 10)  # rounds per second

    def start_firing(self):
        self.running.set()
        if not self.is_alive():
            self.start()

    def stop_firing(self):
        self.running.clear()

    def run(self):
        interval = 1.0 / max(0.001, self.rate)
        while True:
            if self.running.is_set():
                # simple click: down, small sleep, up
                try:
                    self.adapter.left_down()
                    time.sleep(0.01)
                    self.adapter.left_up()
                except Exception:
                    pass
                time.sleep(interval)
            else:
                time.sleep(0.01)


