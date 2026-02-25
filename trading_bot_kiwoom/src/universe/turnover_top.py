from .base import UniverseProvider

class TurnoverTopUniverse(UniverseProvider):
    def __init__(self, symbols, top_n=200):
        self.symbols=symbols; self.top_n=top_n
    def get_symbols(self):
        return self.symbols[:self.top_n]
