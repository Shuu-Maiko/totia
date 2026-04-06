from collections import deque

class History():
    def __init__(self, maxHistory: int = 20):
        self.prev = deque(maxlen=maxHistory)
        self.maxHistory = maxHistory

    def remember(self, user: str, message: str):
        self.prev.append(f"{user} : {message}")
        
    def getHistory(self) -> str:
        return '\n'.join(self.prev)

history = History()
