class UnknownDomain(ValueError):
    def __init__(self, url: str):
        self.url: str = url
