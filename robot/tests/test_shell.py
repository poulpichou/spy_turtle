from robot.shell.shell_controller import ShellController
from robot.simulation.fake_shell_screen import FakeShellScreen
from robot.shell.shell_modes import ShellMode
import time

shell=ShellController(FakeShellScreen())

shell.set_mode(ShellMode.IMAGE_1)
time.sleep(2)

shell.set_mode(ShellMode.STATUS)
time.sleep(2)

shell.event(ShellMode.VIDEO_1,5)

while True:
    shell.update()
    time.sleep(1)