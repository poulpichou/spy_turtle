from fake_oled import FakeOLED
from fake_face import FakeFace
from simulation_engine import SimulationEngine

def main():
    oled = FakeOLED()
    face = FakeFace(oled)
    engine = SimulationEngine(face)
    print("Sim engine ready.")
    engine.idle_loop()

if __name__ == "__main__":
    main()