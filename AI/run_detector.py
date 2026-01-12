# AI/run_detector.py
import time
import cv2
import mss
import numpy as np
import os
import yaml

from AI.core.detector import TargetDetector
from AI.core.mouse_win import get_win32_adapter  # nếu get_win32_adapter tồn tại
from AI.core.aimbot import SmoothAimbot

def load_config():
    cfg_path = os.path.join(os.path.dirname(__file__), "config", "setting.yaml")
    with open(cfg_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def main():
    cfg = load_config()
    model_path = cfg.get("aimbot", {}).get("model_path")
    print("Using model:", model_path)
    detector = TargetDetector(model_path=model_path)
    # nếu mouse_win cung cấp factory get_win32_adapter:
    adapter = None
    try:
        from AI.core.mouse_win import get_win32_adapter
        adapter = get_win32_adapter()
    except Exception:
        pass

    aimbot = SmoothAimbot(smooth_factor=cfg['aimbot']['smooth_aim']['smooth_factor'],
                          max_offset=cfg['aimbot']['smooth_aim']['max_offset'],
                          speed_multiplier=cfg['aimbot']['smooth_aim'].get('base_speed', 1.0))

    sct = mss.mss()
    monitor = sct.monitors[1]
    capture_scale = float(cfg.get("performance", {}).get("capture_scale", 1.0))

    try:
        while True:
            t0 = time.time()
            img = np.array(sct.grab(monitor))  # BGRA
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            scaled = frame
            if capture_scale != 1.0:
                h, w = frame.shape[:2]
                scaled = cv2.resize(frame, (int(w * capture_scale), int(h * capture_scale)))

            detections = detector.detect(scaled, confidence=cfg['aimbot'].get('confidence_threshold', 0.25))
            if capture_scale != 1.0 and detections:
                s = capture_scale
                for d in detections:
                    x1,y1,x2,y2 = d['bbox']
                    d['bbox'] = (int(x1 / s), int(y1 / s), int(x2 / s), int(y2 / s))
                    cx,cy = d['center']
                    d['center'] = (int(cx / s), int(cy / s))

            if detections:
                cx = monitor['width'] // 2
                cy = monitor['height'] // 2
                best = min(detections, key=lambda d: ((d['center'][0]-cx)**2 + (d['center'][1]-cy)**2))
                tx, ty = best['center']
                aimbot.aim_at_target(tx, ty, cx, cy)

            # debug display
            for d in detections:
                x1,y1,x2,y2 = d['bbox']
                cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
                cv2.circle(frame, d['center'], 4, (0,0,255), -1)
            cv2.imshow("Detector Debug", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            dt = time.time() - t0
            if dt < 0.01:
                time.sleep(0.01 - dt)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
