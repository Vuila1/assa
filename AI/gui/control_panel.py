import tkinter as tk
from tkinter import ttk
import threading
import time

from AI.core.detector import TargetDetector
from AI.core.mouse_adapter import get_adapter
from AI.core.aimbot import SmoothAimbot
from AI.core.movement import MovementController
from AI.core.shooting import ShootingThread
from AI.core.overlay import OverlayManager


class ControlPanel:
    def __init__(self, config=None):
        self.root = tk.Tk()
        self.root.title("Aimbot Control Panel (scaffold)")
        self.config = config or {}

        self.adapter = get_adapter(self.config.get("mouse", {}).get("backend", "win32"))
        self.detector = TargetDetector(self.config.get("aimbot", {}).get("model_path"))
        self.aimbot = SmoothAimbot(self.adapter, self.config.get("aimbot", {}))
        self.movement = MovementController(self.config.get("movement", {}))
        self.shooter = ShootingThread(self.config.get("shooting", {}))
        self.overlay = OverlayManager()

        self.running = False
        self._build()

    def _build(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        self.start_btn = ttk.Button(frm, text="Start", command=self.start)
        self.start_btn.grid(row=0, column=0, padx=5, pady=5)

        self.stop_btn = ttk.Button(frm, text="Stop", command=self.stop)
        self.stop_btn.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frm, text="smooth_factor").grid(row=1, column=0, sticky=tk.W)
        self.smooth_var = tk.DoubleVar(value=self.config.get("aimbot", {}).get("smooth_aim", {}).get("smooth_factor", 0.15))
        ttk.Scale(frm, from_=0.01, to=1.0, variable=self.smooth_var, orient=tk.HORIZONTAL, command=self._on_smooth_change).grid(row=1, column=1, sticky=tk.EW)

        ttk.Label(frm, text="base_speed").grid(row=2, column=0, sticky=tk.W)
        self.speed_var = tk.DoubleVar(value=self.config.get("aimbot", {}).get("smooth_aim", {}).get("base_speed", 1.0))
        ttk.Scale(frm, from_=0.1, to=5.0, variable=self.speed_var, orient=tk.HORIZONTAL, command=self._on_speed_change).grid(row=2, column=1, sticky=tk.EW)

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=3)

    def _on_smooth_change(self, _val):
        new = float(self.smooth_var.get())
        self.aimbot.smooth_factor = new

    def _on_speed_change(self, _val):
        new = float(self.speed_var.get())
        self.aimbot.base_speed = new

    def start(self):
        if self.running:
            return
        self.running = True
        self.overlay.start()
        self.shooter.start_firing()
        self._thread = threading.Thread(target=self._main_loop, daemon=True)
        self._thread.start()

    def stop(self):
        if not self.running:
            return
        self.running = False
        self.overlay.stop()
        self.shooter.stop_firing()

    def _get_frame_center(self):
        # naive center of the screen — placeholder
        import ctypes
        user32 = ctypes.windll.user32
        cx = user32.GetSystemMetrics(0) // 2
        cy = user32.GetSystemMetrics(1) // 2
        return cx, cy

    def _main_loop(self):
        while self.running:
            # capture frame and detect (placeholder detector returns empty list)
            detections = []
            # for scaffold we don't capture; detector returns []
            # update overlay
            self.overlay.update_detections(detections)

            # If we had targets, pick first and aim
            if detections:
                target = detections[0]
                pred_x, pred_y = self.movement.predict_target(target)
                target_point = {"x": pred_x, "y": pred_y}
                self.aimbot.aim_and_lock(target_point, self._get_frame_center)

            time.sleep(0.01)

    def run(self):
        self.root.mainloop()
