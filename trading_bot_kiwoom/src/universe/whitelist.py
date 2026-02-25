from .base import UniverseProvider

class WhitelistUniverse(UniverseProvider):
    def __init__(self, symbols): self.symbols=symbols
    def get_symbols(self): return list(self.symbols)
