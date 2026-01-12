class TargetDetector:
    """Placeholder detector. Replace with real model-based detector later.

    detect(frame, confidence=0.5) should return a list of detections where
    each detection is a dict like: {"x": x, "y": y, "w": w, "h": h, "score": s}
    """

    def __init__(self, model_path=None):
        self.model_path = model_path

    def detect(self, frame, confidence=0.5):
        # Placeholder: return empty list so the rest of the scaffold can run.
        return []
