"""Simple interface wrapper for the aimbot.

This is a placeholder for a GUI or CLI layer. Replace with actual UI code.
"""
from ..core import AimbotEngine

class AimbotInterface:
    def __init__(self, config=None):
        self.engine = AimbotEngine(config=config)

    def run(self):
        """Run a minimal interactive loop (placeholder)."""
        self.engine.start()
        try:
            print("Aimbot engine started (placeholder). Press Ctrl+C to stop.")
            while True:
                # In a real app, update UI and draw frames
                break
        finally:
            self.engine.stop()

    def stop(self):
        self.engine.stop()
