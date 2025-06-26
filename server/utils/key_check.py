# server/utils/key_check.py

import os

KEYS_FILE_PATH = os.path.join(os.path.dirname(__file__), '../../keys.txt')

class KeyManager:
    def __init__(self, keys_file=KEYS_FILE_PATH):
        self.keys_file = keys_file
        self.keys_data = {}
        self.load_keys()

    def load_keys(self):
        """
        Loads keys and their slots from keys.txt file.
        Expected file format per line: key_string,slots
        Example:
          abc123,3
          def456,1
        """
        self.keys_data.clear()
        try:
            with open(self.keys_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    parts = line.split(',')
                    if len(parts) != 2:
                        continue
                    key = parts[0].strip()
                    try:
                        slots = int(parts[1].strip())
                    except ValueError:
                        continue
                    self.keys_data[key] = slots
        except FileNotFoundError:
            # Could raise or just log
            print(f"[Warning] keys.txt file not found at {self.keys_file}")

    def validate_key(self, key):
        """
        Returns True if key exists and has slots > 0
        """
        return key in self.keys_data and self.keys_data[key] > 0

    def get_slots(self, key):
        """
        Returns number of slots for the key or 0 if invalid
        """
        return self.keys_data.get(key, 0)

    def decrement_slot(self, key):
        """
        Decrement the slot count for a key when a slot is used.
        Returns True if successful, False if no slots left or invalid key.
        """
        if self.validate_key(key) and self.keys_data[key] > 0:
            self.keys_data[key] -= 1
            self._save_keys()
            return True
        return False

    def increment_slot(self, key):
        """
        Increment the slot count for a key when a slot is freed.
        """
        if key in self.keys_data:
            self.keys_data[key] += 1
            self._save_keys()
            return True
        return False

    def _save_keys(self):
        """
        Save the current keys_data back to keys.txt.
        """
        try:
            with open(self.keys_file, 'w') as f:
                for key, slots in self.keys_data.items():
                    f.write(f"{key},{slots}\n")
        except Exception as e:
            print(f"[Error] Failed to save keys to {self.keys_file}: {e}")

# Usage example (remove or comment out in production):
# if __name__ == "__main__":
#     km = KeyManager()
#     print(km.keys_data)
#     print(km.validate_key("abc123"))
#     print(km.get_slots("abc123"))
