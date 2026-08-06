# Optional motor encoders

Encoder support is prepared but disabled by default:

```python
MOTOR_ENCODERS_ENABLED=False
```

With this value, Spy Turtle behaves exactly as before and does not reserve encoder GPIOs.

Future allocation:
- left encoder A/B: GPIO22/GPIO23
- right encoder A/B: GPIO14/GPIO15

Before enabling, confirm the motor encoder voltage and determine `MOTOR_ENCODER_PULSES_PER_REV`. GPIO14/GPIO15 are also UART pins, so UART must not be using them when encoders are enabled.

When enabled, `/state` includes ticks, revolutions and distance. Revolutions/distance remain `null` while pulses per revolution is `0`.
