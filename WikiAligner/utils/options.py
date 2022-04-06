class Options:
    def __init__(self, name, command) -> None:
        self.name = name
        self.command = command

    def choose(self):
        self.command()

    def __str__(self) -> str:
        return self.name