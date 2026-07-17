class FakeEyesDisplay:
    def __init__(self, name):
        self.name = name
        self.current = None

        print(f"[FakeEyesDisplay] {name} ready")

    def show(self, bitmap):
        self.current = bitmap

        print("")
        print(f"--- {self.name} eye ---")

        for line in bitmap:
            print(line)

        print("----------------")