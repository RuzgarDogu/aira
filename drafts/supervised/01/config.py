import json
import os

class Config:
    def __init__(self, file=None):
        if file:
            file = os.path.join(os.path.dirname(__file__), 'configs', file)
            with open(file, 'r') as f:
                data = json.load(f)
                for key, value in data.items():
                    setattr(self, key, value)

    @property
    def close_index(self):
        return self.state_keys.index('close')
    
    @property
    def normalize(self):
        return self._normalize == "True"
    
    @property
    def schedule_learning_rate(self):
        return self._schedule_learning_rate == "True"
    
    @property
    def learning_rate(self):
        return self._learning_rate * 10 if self.schedule_learning_rate else self._learning_rate
    
