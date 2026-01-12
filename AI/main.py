import os
import yaml
import threading
from AI.gui.control_panel import ControlPanel

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "setting.yaml")


def load_config(path=CONFIG_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    config = load_config()
    panel = ControlPanel(config=config)
    panel.run()


if __name__ == "__main__":
    main()
