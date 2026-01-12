import time
import math

class SmoothAimbot:
    def __init__(self, adapter, config):
        self.adapter = adapter
        self.config = config or {}
        self.smooth = self.config.get("smooth_aim", {})
        self.smooth_factor = self.smooth.get("smooth_factor", 0.15)
        self.max_offset = self.smooth.get("max_offset", 200)
        self.base_speed = self.smooth.get("base_speed", 1.0)
        self.lock_mode = self.config.get("lock_mode", False)
        self.locked_target = None

    def aim_at_target(self, target_x, target_y, center_x, center_y):
        """Compute required movement and apply smoothing before moving the mouse."""
        dx = target_x - center_x
        dy = target_y - center_y

        # Clamp
        dist = math.hypot(dx, dy)
        if dist > self.max_offset:
            scale = self.max_offset / dist
            dx *= scale
            dy *= scale

        # Apply smooth factor and base speed
        move_x = dx * self.smooth_factor * self.base_speed
        move_y = dy * self.smooth_factor * self.base_speed

        # Convert to integers and perform move
        self.adapter.move_relative(int(move_x), int(move_y))

    def aim_and_lock(self, target, get_frame_center, timeout=0.1):
        """Aim at a target and optionally lock onto it. Target is dict with x,y.

        get_frame_center is a callable returning (cx, cy)
        """
        if not target:
            self.locked_target = None
            return

        cx, cy = get_frame_center()
        self.aim_at_target(target["x"], target["y"], cx, cy)

        if self.lock_mode:
            # Simple lock: if close enough set locked_target
            dx = target["x"] - cx
            dy = target["y"] - cy
            if math.hypot(dx, dy) < self.config.get("lock_threshold", 4):
                self.locked_target = target
        else:
            self.locked_target = None

    def update_config(self, new_config):
        self.config.update(new_config or {})
        self.smooth = self.config.get("smooth_aim", self.smooth)
        self.smooth_factor = self.smooth.get("smooth_factor", self.smooth_factor)
        self.max_offset = self.smooth.get("max_offset", self.max_offset)
        self.base_speed = self.smooth.get("base_speed", self.base_speed)
        self.lock_mode = self.config.get("lock_mode", self.lock_mode)


