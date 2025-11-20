from collections import deque

class History():
    def __init__(self, max_history = 20):
        self.prev = deque(maxlen=max_history)
        self.max_history = max_history

    def remember(self, user , message):
        self.prev.append(f"{user} : {message}")
        
    def get_history(self):
        print('\n'.join(self.prev))
        return '\n'.join(self.prev)


history = History()
    
