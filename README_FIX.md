# Camera/Admin frontend fix

- Serializes access to the shared Picamera2 instance.
- Retries once after a broken camera pipe.
- Accepts an empty HTTP response for reboot, shutdown and restart commands.

The RGB and temporary thermal endpoints can now share the same physical camera safely.
