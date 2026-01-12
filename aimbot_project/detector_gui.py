"""
Minimal detector GUI (single-file)

- Uses ultralytics YOLO if available (optional).
- Falls back to a lightweight contour-based detector when ultralytics is not installed.

Usage:
    python detector_gui.py

This script provides a small tkinter GUI to:
- Load an image
- Start/stop webcam preview
- Run a single-frame detection and overlay bounding boxes

This file is intentionally minimal and dependency-light. If you want better detection, install
ultralytics (pip install ultralytics) and have a YOLO model available (e.g. yolov8n.pt).
"""

import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np

# Try to import ultralytics (optional). If available, we'll use it for inference.
try:
    from ultralytics import YOLO
    _HAS_ULTRALYTICS = True
except Exception:
    YOLO = None
    _HAS_ULTRALYTICS = False


class Detector:
    """Simple detector wrapper. Tries to use ultralytics YOLO if present,
    otherwise falls back to a naive contour-based detector.
    """

    def __init__(self, model_path: str = 'yolov8n.pt'):
        self.model = None
        if _HAS_ULTRALYTICS:
            try:
                # Attempt to create a YOLO model. This will download weights if needed.
                self.model = YOLO(model_path)
                print(f'Loaded YOLO model: {model_path}')
            except Exception as e:
                print('Failed to load ultralytics YOLO model:', e)
                self.model = None

    def detect(self, frame):
        """Detect objects in a BGR OpenCV frame.

        Returns a list of boxes: [ (x1,y1,x2,y2,score,class_id), ... ]
        Coordinates are integers.
        """
        if self.model is not None:
            try:
                # ultralytics expects either a path or an image in RGB
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.model(rgb)
                res = results[0]
                boxes_out = []
                if hasattr(res, 'boxes') and res.boxes is not None:
                    # res.boxes.xyxy, res.boxes.conf, res.boxes.cls
                    xyxy = res.boxes.xyxy.cpu().numpy()
                    conf = res.boxes.conf.cpu().numpy()
                    cls = res.boxes.cls.cpu().numpy()
                    for (x1, y1, x2, y2), c, cl in zip(xyxy, conf, cls):
                        boxes_out.append((int(x1), int(y1), int(x2), int(y2), float(c), int(cl)))
                return boxes_out
            except Exception as e:
                print('Ultralytics detection error:', e)
                # Fall through to fallback detector

        # Fallback: simple contour detector on grayscale + threshold
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (7, 7), 0)
        _, th = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        boxes = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w * h < 500:  # skip small areas
                continue
            # Use a dummy score and class id
            boxes.append((x, y, x + w, y + h, 0.5, 0))
        return boxes


def draw_boxes(frame, boxes, class_names=None):
    out = frame.copy()
    for box in boxes:
        x1, y1, x2, y2, score, cls = box
        label = f'{cls}:{score:.2f}' if class_names is None else f'{class_names.get(cls, str(cls))}:{score:.2f}'
        cv2.rectangle(out, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(out, label, (x1, max(15, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    return out


class DetectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('Simple Detector GUI')

        self.detector = Detector()
        self.frame = None
        self.previewing = False
        self.cap = None
        self.preview_thread = None

        self._build_ui()

    def _build_ui(self):
        frm = tk.Frame(self.root)
        frm.pack(padx=8, pady=8)

        btn_load = tk.Button(frm, text='Load Image', width=20, command=self.load_image)
        btn_load.grid(row=0, column=0, padx=4, pady=4)

        btn_cam = tk.Button(frm, text='Start Camera', width=20, command=self.toggle_camera)
        btn_cam.grid(row=0, column=1, padx=4, pady=4)

        btn_detect = tk.Button(frm, text='Run Detection (single)', width=20, command=self.run_detection_single)
        btn_detect.grid(row=1, column=0, padx=4, pady=4)

        btn_stop = tk.Button(frm, text='Stop Preview', width=20, command=self.stop_preview)
        btn_stop.grid(row=1, column=1, padx=4, pady=4)

        lbl = tk.Label(self.root, text='Notes: Uses ultralytics YOLO if installed; otherwise a simple fallback detector.')
        lbl.pack(padx=8, pady=(0, 8))

    def load_image(self):
        path = filedialog.askopenfilename(title='Select an image', filetypes=[('Images', '*.png *.jpg *.jpeg *.bmp'), ('All files', '*.*')])
        if not path:
            return
        img = cv2.imread(path)
        if img is None:
            messagebox.showerror('Error', 'Failed to load image')
            return
        self.frame = img
        display = cv2.resize(img, (800, int(img.shape[0] * 800 / max(1, img.shape[1]))))
        cv2.imshow('Detector - Image', display)

    def toggle_camera(self):
        if self.previewing:
            self.stop_preview()
            return
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror('Error', 'Failed to open camera')
            return
        self.previewing = True
        self.preview_thread = threading.Thread(target=self._camera_loop, daemon=True)
        self.preview_thread.start()

    def _camera_loop(self):
        while self.previewing and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            self.frame = frame
            display = cv2.resize(frame, (800, int(frame.shape[0] * 800 / max(1, frame.shape[1]))))
            cv2.imshow('Detector - Camera', display)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.stop_preview()
                break
        self.stop_preview()

    def stop_preview(self):
        self.previewing = False
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None
        try:
            cv2.destroyWindow('Detector - Camera')
            cv2.destroyWindow('Detector - Image')
        except Exception:
            pass

    def run_detection_single(self):
        if self.frame is None:
            messagebox.showinfo('Info', 'No frame available. Load an image or start the camera first.')
            return
        # Run detection on a copy to avoid race conditions with camera thread
        frame_copy = self.frame.copy()
        boxes = self.detector.detect(frame_copy)
        out = draw_boxes(frame_copy, boxes)
        cv2.imshow('Detector - Results', out)


def main():
    root = tk.Tk()
    app = DetectorGUI(root)
    root.protocol('WM_DELETE_WINDOW', lambda: (app.stop_preview(), root.destroy()))
    root.mainloop()


if __name__ == '__main__':
    main()
