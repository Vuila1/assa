"""Project entrypoint for the aimbot package."""
from .gui.interface import AimbotInterface
from .utils.helpers import load_config


def main(config_path: str | None = None):
    config = {}
    if config_path:
        config = load_config(config_path)
    app = AimbotInterface(config=config)
    app.run()


if __name__ == "__main__":
    import sys
    cfg = sys.argv[1] if len(sys.argv) > 1 else None
    main(cfg)
