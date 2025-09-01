

class Flag:
    def __init__(self, value:int = 0):
        if isinstance(value, float):
            value = int(value)
        self.value = value

    def __str__(self):
        return str(self.value)

    def __int__(self):
        return self.value

    def get(self):
        return self.value

    def set(self, value:int):
        if isinstance(value, float):
            value = int(value)
        self.value = value

    def has(self, key:int):
        if isinstance(key, float):
            key = int(key)
        return bool(self.value & key)

    def add(self, key:int):
        if isinstance(key, float):
            key = int(key)
        self.value = self.value | key

    def remove(self, key:int):
        if isinstance(key, float):
            key = int(key)
        self.value &= ~key
