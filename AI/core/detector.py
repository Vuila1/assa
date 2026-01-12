# AI/core/detector.py
# Detector implementation using ultralytics YOLO (.pt). Expects BGR numpy frames.

import os
from ultralytics import YOLO
import numpy as np

class TargetDetector:
    def __init__(self, model_path=None, device=None):
        """
        model_path: path to .pt file
        device: e.g. '0' for GPU 0, or 'cpu' for CPU. If None, ultralytics auto-detects.
        """
        self.model_path = model_path or os.path.join(os.path.dirname(__file__), '..', 'models', 'yolo11m.pt')
        self.device = device
        try:
            if self.device:
                self.model = YOLO(self.model_path, device=self.device)
            else:
                self.model = YOLO(self.model_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load YOLO model at {self.model_path}: {e}")

    def detect(self, frame, confidence=0.25, imgsz=None):
        """
        Run detection on BGR frame (numpy array).
        Returns list of detections: each is dict with keys:
            'bbox': (x1, y1, x2, y2),
            'center': (cx, cy),
            'confidence': float,
            'class': int or str
        """
        if frame is None:
            return []
        try:
            results = self.model.predict(source=frame, conf=confidence, imgsz=imgsz, verbose=False)
            r = results[0]
        except Exception as e:
            print("Detector predict error:", e)
            return []

        detections = []
        try:
            boxes = getattr(r, "boxes", None)
            if boxes is None:
                return []
            xyxy = boxes.xyxy.cpu().numpy() if hasattr(boxes.xyxy, "cpu") else boxes.xyxy
            confs = boxes.conf.cpu().numpy() if hasattr(boxes.conf, "cpu") else boxes.conf
            clses = boxes.cls.cpu().numpy() if hasattr(boxes.cls, "cpu") else boxes.cls
            for b, c, cls in zip(xyxy, confs, clses):
                x1, y1, x2, y2 = int(b[0]), int(b[1]), int(b[2]), int(b[3])
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                detections.append({
                    "bbox": (x1, y1, x2, y2),
                    "center": (cx, cy),
                    "confidence": float(c),
                    "class": int(cls)
                })
        except Exception as e:
            try:
                data = getattr(r, "boxes").data
                arr = data.cpu().numpy() if hasattr(data, "cpu") else np.array(data)
                for row in arr:
                    x1, y1, x2, y2, conf, cls = row[:6]
                    x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))
                    cx, cy = (x1+x2)//2, (y1+y2)//2
                    detections.append({
                        "bbox": (x1, y1, x2, y2),
                        "center": (cx, cy),
                        "confidence": float(conf),
                        "class": int(cls)
                    })
            except Exception as ee:
                print("Detector parse error:", ee)
                return []

        return detections
