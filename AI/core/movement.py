import math

class Prediction:
    @staticmethod
    def predict(px, py, vx, vy, dt=0.1):
        """Simple linear prediction: new position after dt seconds."""
        return px + vx * dt, py + vy * dt


class MovementController:
    def __init__(self, config=None):
        self.config = config or {}

    def predict_target(self, detection, dt=0.05):
        # detection may contain vx, vy or previous positions
        x = detection.get("x", 0)
        y = detection.get("y", 0)
        vx = detection.get("vx", 0)
        vy = detection.get("vy", 0)
        return Prediction.predict(x, y, vx, vy, dt)


