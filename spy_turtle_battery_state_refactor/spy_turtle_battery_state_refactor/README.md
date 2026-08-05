# Spy Turtle Battery & State Refactor

This patch replaces the fixed `87%` battery value with live UPS HAT readings and restructures `/state`.

## Changed files

- `robot/system/state.py`
- `robot/system/robot.py`
- `robot/api/app.py`
- `robot/shell/ui/shell_views.py`
- `robot/shell/ui/widgets.py`
- `frontend/index.html`
- `frontend/js/dashboard.js`
- `frontend/js/center.js`

## Install

From the repository root:

```bash
cp -r /path/to/spy_turtle_battery_state_refactor/robot/* robot/
cp -r /path/to/spy_turtle_battery_state_refactor/frontend/* frontend/
python3 -m py_compile robot/system/state.py robot/system/robot.py robot/api/app.py robot/shell/ui/shell_views.py robot/shell/ui/widgets.py
sudo systemctl restart spyturtle
curl -s http://localhost:8000/state | python3 -m json.tool
```

Automatic shutdown is deliberately not enabled yet. First validate live readings over one charge/discharge cycle.
