"""
Launcher GUI for the aimbot project.
Provides Start, Stop, Settings and Select Model functionality.
Saves settings to a JSON file in the project directory.
"""

import json
import os
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "launcher_settings.json")


class LauncherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Aimbot Launcher")
        self.root.geometry("480x240")
        self.root.resizable(False, False)

        self.running_event = threading.Event()
        self.worker_thread = None

        # Default settings
        self.settings = {
            "model_path": "",
            "confidence_threshold": 0.5,
            "hotkey": "F6",
            "auto_start": False,
        }
        self._load_settings()

        self._build_ui()

        if self.settings.get("auto_start"):
            self.start()

    def _build_ui(self):
        pad = 10
        main_frame = ttk.Frame(self.root, padding=pad)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top: model selection
        model_frame = ttk.LabelFrame(main_frame, text="Model", padding=(pad, 8))
        model_frame.pack(fill=tk.X, padx=pad, pady=(pad, 6))

        self.model_var = tk.StringVar(value=self.settings.get("model_path", ""))
        model_entry = ttk.Entry(model_frame, textvariable=self.model_var, state="readonly", width=50)
        model_entry.pack(side=tk.LEFT, padx=(0, 6), pady=4, expand=True, fill=tk.X)

        select_btn = ttk.Button(model_frame, text="Select Model", command=self.select_model)
        select_btn.pack(side=tk.LEFT, padx=(6, 0))

        # Middle: status and controls
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, padx=pad, pady=(6, 6))

        self.status_var = tk.StringVar(value="Stopped")
        status_label = ttk.Label(status_frame, text="Status:")
        status_label.pack(side=tk.LEFT)
        status_value = ttk.Label(status_frame, textvariable=self.status_var, foreground="red")
        status_value.pack(side=tk.LEFT, padx=(6, 0))

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, padx=pad, pady=(6, 6))

        self.start_btn = ttk.Button(btn_frame, text="Start", command=self.start, width=12)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self.stop, width=12)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.stop_btn.state(["disabled"])  # Initially disabled

        settings_btn = ttk.Button(btn_frame, text="Settings", command=self.open_settings, width=12)
        settings_btn.pack(side=tk.LEFT, padx=(0, 8))

        quit_btn = ttk.Button(btn_frame, text="Quit", command=self._on_quit, width=12)
        quit_btn.pack(side=tk.RIGHT)

        # Bottom: quick settings preview
        preview_frame = ttk.LabelFrame(main_frame, text="Settings Preview", padding=(pad, 8))
        preview_frame.pack(fill=tk.BOTH, padx=pad, pady=(6, 0), expand=True)

        self.preview_text = tk.Text(preview_frame, height=4, wrap=tk.WORD, state=tk.DISABLED)
        self.preview_text.pack(fill=tk.BOTH, expand=True)

        self._update_preview()

    def select_model(self):
        filetypes = [("Model files", "*.pt *.pth *.onnx"), ("All files", "*")]
        path = filedialog.askopenfilename(title="Select Model", initialdir=".", filetypes=filetypes)
        if path:
            self.model_var.set(path)
            self.settings["model_path"] = path
            self._save_settings()
            self._update_preview()

    def open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.resizable(False, False)
        pad = 8

        frm = ttk.Frame(win, padding=pad)
        frm.pack(fill=tk.BOTH, expand=True)

        # Confidence threshold
        ttk.Label(frm, text="Confidence threshold:").grid(row=0, column=0, sticky=tk.W, pady=(0, 6))
        conf_var = tk.DoubleVar(value=self.settings.get("confidence_threshold", 0.5))
        conf_scale = ttk.Scale(frm, from_=0.0, to=1.0, orient=tk.HORIZONTAL, variable=conf_var)
        conf_scale.grid(row=0, column=1, sticky=tk.EW, padx=(8, 0), pady=(0, 6))

        # Hotkey
        ttk.Label(frm, text="Toggle Hotkey:").grid(row=1, column=0, sticky=tk.W, pady=(0, 6))
        hotkey_var = tk.StringVar(value=self.settings.get("hotkey", "F6"))
        hotkey_entry = ttk.Entry(frm, textvariable=hotkey_var)
        hotkey_entry.grid(row=1, column=1, sticky=tk.EW, padx=(8, 0), pady=(0, 6))

        # Auto-start
        auto_var = tk.BooleanVar(value=self.settings.get("auto_start", False))
        auto_chk = ttk.Checkbutton(frm, text="Auto start on launch", variable=auto_var)
        auto_chk.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(0, 6))

        # Buttons
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=(8, 0))

        def save_and_close():
            self.settings["confidence_threshold"] = float(conf_var.get())
            self.settings["hotkey"] = hotkey_var.get()
            self.settings["auto_start"] = bool(auto_var.get())
            self._save_settings()
            self._update_preview()
            win.destroy()

        save_btn = ttk.Button(btn_frame, text="Save", command=save_and_close)
        save_btn.pack(side=tk.RIGHT, padx=(8, 0))

        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=win.destroy)
        cancel_btn.pack(side=tk.RIGHT)

        # Make second column expand
        frm.columnconfigure(1, weight=1)

    def _update_preview(self):
        text = (
            f"Model: {self.settings.get('model_path', '') or '<not selected>'}\n"
            f"Confidence threshold: {self.settings.get('confidence_threshold', 0.5)}\n"
            f"Hotkey: {self.settings.get('hotkey', 'F6')}\n"
            f"Auto start: {self.settings.get('auto_start', False)}\n"
        )
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert(tk.END, text)
        self.preview_text.config(state=tk.DISABLED)

    def _load_settings(self):
        try:
            if os.path.exists(SETTINGS_PATH):
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.settings.update(data)
        except Exception:
            # ignore load errors, keep defaults
            pass

    def _save_settings(self):
        try:
            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            messagebox.showwarning("Save Settings", f"Failed to save settings: {e}")

    def start(self):
        if self.worker_thread and self.worker_thread.is_alive():
            messagebox.showinfo("Already running", "The aimbot is already running.")
            return

        model = self.settings.get("model_path")
        if not model:
            if not messagebox.askyesno("No model selected", "No model selected. Continue anyway?"):
                return

        # Start worker thread
        self.running_event.set()
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

        self.status_var.set("Running")
        self._set_running_state(True)

    def stop(self):
        if not (self.worker_thread and self.worker_thread.is_alive()):
            return
        self.running_event.clear()
        # Give the thread a moment to exit
        self.worker_thread.join(timeout=2.0)
        self.status_var.set("Stopped")
        self._set_running_state(False)

    def _set_running_state(self, running: bool):
        if running:
            self.start_btn.state(["disabled"])
            self.stop_btn.state(["!disabled"])
            # status text color
            # note: using label foreground requires updating via config, we update the var only
        else:
            self.start_btn.state(["!disabled"])
            self.stop_btn.state(["disabled"])

    def _worker_loop(self):
        # Placeholder for the real aimbot loop.
        # Replace with actual loading and running of the model.
        try:
            model_path = self.settings.get("model_path")
            conf = self.settings.get("confidence_threshold", 0.5)

            # Simulated load
            print(f"[launcher] Loading model: {model_path} (confidence={conf})")
            for i in range(3):
                if not self.running_event.is_set():
                    print("[launcher] Startup cancelled")
                    return
                time.sleep(0.4)

            # Run loop
            while self.running_event.is_set():
                # Simulate doing some work
                # In a real integration, you'd call into the aimbot main loop here.
                print("[launcher] Running aimbot tick...")
                time.sleep(1.0)
        except Exception as e:
            # Report error to user
            messagebox.showerror("Runtime Error", f"An error occurred in the aimbot thread:\n{e}")
        finally:
            # Ensure UI reflects stopped state
            self.running_event.clear()
            # Tk UI updates must be scheduled on main thread
            try:
                self.root.after(0, lambda: (self.status_var.set("Stopped"), self._set_running_state(False)))
            except Exception:
                pass

    def _on_quit(self):
        if self.worker_thread and self.worker_thread.is_alive():
            if not messagebox.askyesno("Quit", "Aimbot is running. Stop and quit?"):
                return
            self.stop()
        self.root.quit()


def main():
    root = tk.Tk()
    # Use ttk themed widgets
    try:
        from ttkthemes import ThemedTk  # optional dependency; not required
    except Exception:
        pass

    app = LauncherGUI(root)
    root.protocol("WM_DELETE_WINDOW", app._on_quit)
    root.mainloop()


if __name__ == "__main__":
    main()
