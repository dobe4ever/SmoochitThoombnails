import json

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def save_json(path, file):
    with open(path, "w") as f:
        f.write(json.dumps(file, indent=4))
