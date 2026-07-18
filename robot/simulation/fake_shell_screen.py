class FakeShellScreen:
    def __init__(self):
        print("[FakeShellScreen] ready")

    def show_image(self,path):
        print(f"[Shell] image {path}")

    def show_text(self,title,lines):
        print(f"[Shell] {title}")
        for line in lines:
            print(line)

    def clear(self):
        print("[Shell] clear")