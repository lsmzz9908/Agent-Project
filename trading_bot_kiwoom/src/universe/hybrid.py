from .whitelist import WhitelistUniverse

class HybridUniverse:
    def __init__(self, whitelist_symbols):
        self.whitelist=WhitelistUniverse(whitelist_symbols)
    def get_symbols(self):
        return self.whitelist.get_symbols()
