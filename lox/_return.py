class ReturnJmp(RuntimeError):
    def __init__(self, value):
        super().__init__()
        self.value = value