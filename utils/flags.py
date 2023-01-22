

class Flag:
    def __init__(self, value:int = 0):
        self.value = value

    def __str__(self):
        return str(self.value)

    def get(self):
        return self.value

    def set(self, value:int):
        self.value = value

    def has(self, key:int):
        return bool(self.value & key)

    def add(self, key:int):
        self.value = self.value | key

    def remove(self, key:int):
        self.value &= ~key
