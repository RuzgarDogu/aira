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
    def calculate_fee(self):
        return self._calculate_fee == "True"

    @property
    def transaction_fee(self):
        return self._transaction_fee if self.calculate_fee else 0
    
    @property
    def print_log(self):
        return self._print_log == "True"
    
