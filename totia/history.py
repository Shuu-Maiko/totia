import datetime
from collections import deque

class History():
    def __init__(self, maxHistory: int = 20):
        self.prev = deque(maxlen=maxHistory)
        self.maxHistory = maxHistory

    def remember(self, user: str, message: str):
        timestamp = datetime.datetime.now().strftime("%h %d, %I:%M %p")
        self.prev.append(f"[{timestamp}] {user} : {message}")
        
    def getHistory(self) -> str:
        return '\n'.join(self.prev)

history = History()
