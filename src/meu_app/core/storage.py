import os
import json

# ==============================================================================
# Persistência de Dados (FileStorage)
# ==============================================================================

class FileStorage:
    def __init__(self, base_dir=".src/data"):
        self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    def read_json(self, file_name, default_value):
        path = os.path.join(self.base_dir, file_name)
        try:
            if not os.path.exists(path):
                self.write_json(file_name, default_value)
                return default_value
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            self.write_json(file_name, default_value)
            return default_value

    def write_json(self, file_name, data):
        path = os.path.join(self.base_dir, file_name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def read_text_file(self, file_name, default_value):
        path = os.path.join(self.base_dir, file_name)
        try:
            if not os.path.exists(path):
                self.write_text_file(file_name, default_value)
                return default_value
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            self.write_text_file(file_name, default_value)
            return default_value

    def write_text_file(self, file_name, content):
        path = os.path.join(self.base_dir, file_name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def append_text_file(self, file_name, content):
        path = os.path.join(self.base_dir, file_name)
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)