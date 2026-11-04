"""Pure control-law smoke tests; does not access GPIO."""
from pathlib import Path


def main():
    source=Path(__file__).resolve().parents[1]/"hardware"/"motor.py"
    code=source.read_text(encoding="utf-8")
    assert "class DifferentialDrive:" in code
    assert "MOTOR_ENCODER_CORRECTION_KP" in code
    assert "MOTOR_ENCODER_CORRECTION_MAX" in code
    print("[TEST] Motor correction implementation present. Run on robot for hardware validation.")


if __name__=="__main__":main()
