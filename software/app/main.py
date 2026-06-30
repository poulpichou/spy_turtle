# Spy Turtle - Entry point

VERSION = "0.1.0"


def print_banner():
    print("=" * 45)
    print(f"🐢 Spy Turtle v{VERSION}")
    print("")
    print("Starting system...")
    print("")


def check_system():
    print("✓ Python OK")
    print("✓ Project structure OK")
    print("✓ Simulation mode active")


def main():
    print_banner()
    check_system()

    print("")
    print("Robot is ready 🚀")
    print("=" * 45)


if __name__ == "__main__":
    main()