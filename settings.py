import os
try:
    import yaml
except Exception:
    yaml = None

DEFAULT_SETTINGS = {
    "fps": 15,
    "speeds": {"slow": 8, "normal": 15, "fast": 24},
    "colors": {"snake": (0, 255, 0), "food": (255, 255, 255), "bg": (0, 0, 0)}
}

def parse_color(value):
    if value is None:
        return (0, 0, 0)
    if isinstance(value, (list, tuple)) and len(value) == 3:
        return tuple(int(x) for x in value)
    if isinstance(value, str):
        v = value.strip()
        if v.startswith("#") and len(v) == 7:
            return tuple(int(v[i:i+2], 16) for i in (1, 3, 5))
        parts = [p.strip() for p in v.split(",")]
        if len(parts) == 3:
            return tuple(int(p) for p in parts)
    return (0, 0, 0)

def load_settings(path="settings.yaml"):
    settings = DEFAULT_SETTINGS.copy()
    settings["colors"] = DEFAULT_SETTINGS["colors"].copy()
    settings["speeds"] = DEFAULT_SETTINGS["speeds"].copy()

    if not os.path.exists(path):
        return settings

    try:
        if yaml:
            with open(path, "r") as f:
                data = yaml.safe_load(f) or {}
        else:
            data = {}
            with open(path, "r") as f:
                for line in f:
                    line = line.partition("#")[0].strip()
                    if not line or ":" not in line:
                        continue
                    k, v = line.split(":", 1)
                    data[k.strip()] = v.strip()
    except Exception:
        return settings

    if "fps" in data:
        try:
            settings["fps"] = int(data["fps"])
        except Exception:
            pass

    if "speeds" in data and isinstance(data["speeds"], dict):
        for k, v in data["speeds"].items():
            try:
                settings["speeds"][k] = int(v)
            except Exception:
                pass

    colors = data.get("colors") or {}
    if isinstance(colors, dict):
        for k in ("snake", "food", "bg"):
            if k in colors:
                settings["colors"][k] = parse_color(colors[k])

    return settings