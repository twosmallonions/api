class Repository:
    connection_timeout: int

    def __init__(self, connection_timeout: int = 10) -> None:
        self.connection_timeout = connection_timeout
