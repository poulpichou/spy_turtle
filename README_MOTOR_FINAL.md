# Final motor integration

Motor configuration is now isolated in `robot/config/motors.py`.

The right motor is inverted because both motors are mounted as mirror images.

The existing frontend movement controls continue to use:

```json
{"type":"move","value":"forward"}
```

The API also accepts an optional speed:

```json
{"type":"move","value":"forward","extra":{"speed":0.7}}
```

Available movement values are `forward`, `backward`, `left`, `right`, and `stop`.

Runtime inspection:

```bash
curl http://localhost:8000/state
curl http://localhost:8000/motors/config
```

`/state` now includes the effective left/right motor speeds and inversion settings.

The geometry and encoder values in `robot/config/motors.py` prepare the next encoder phase. Until encoders are connected, `DISTANCE_STEP_MM` and `TURN_STEP_DEGREES` are state estimates rather than measured odometry.
