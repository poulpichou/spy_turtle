# Motor update

This package adds the real TB6612FNG differential-drive implementation.

## Wiring

### Channel A / left motor

| TB6612 | Raspberry Pi |
|---|---|
| STBY | GPIO5 |
| PWMA | GPIO12 |
| AIN1 | GPIO6 |
| AIN2 | GPIO13 |

Motor red/white wires connect to AO1/AO2.

### Channel B / right motor

| TB6612 | Raspberry Pi |
|---|---|
| PWMB | GPIO26 |
| BIN1 | GPIO16 |
| BIN2 | GPIO20 |

Motor red/white wires connect to BO1/BO2.

### Power

- VCC -> Raspberry Pi 3.3 V
- VM -> 5 V power rail from the UPS USB output
- All grounds must be common
- Encoder wires remain disconnected for now

## Test

Stop Spy Turtle before testing:

```bash
./scripts/stop_turtle.sh
python -m robot.tests.test_motors --channel a
python -m robot.tests.test_motors --channel b
python -m robot.tests.test_motors --channel both
```

If one mounted wheel runs backwards, change its corresponding `MOTOR_*_INVERTED` setting to `True`.
