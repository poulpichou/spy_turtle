Unix Cheat Sheet
Files
``` bash
pwd                 # Current directory
ll                  # Detailed listing
tree -L 2           # Directory tree (2 levels)
find . -name "*.py" # Find files
grep -R "text" .    # Search recursively
cat file            # Display file
less file           # Scroll file
tail -f logs/log    # Follow log in real time
du -sh .            # Folder size
df -h               # Free disk space
```
Processes
``` bash
ps aux              # Running processes
pgrep -af python    # Find Python processes
top                 # Live CPU/RAM
htop                # Better top (if installed)
kill PID            # Stop process
pkill -f robot      # Stop matching process
```
System
``` bash
hostnamectl         # Host information
uptime              # Uptime + load
free -h             # RAM usage
lsblk               # Disks
mount               # Mounted filesystems
vcgencmd measure_temp      # CPU temp (~40-70°C normal)
vcgencmd get_throttled     # Expect: throttled=0x0
```
GPIO / Hardware
``` bash
gpioinfo            # GPIO allocation
i2cdetect -y 1      # Expect: 2d,3c,3d
i2cget -y 1 0x2d 0x00 # Read UPS register
ls /dev/spi*        # SPI devices
dmesg | tail -100   # Kernel errors
journalctl -xe      # System errors
```
Camera / Audio
``` bash
rpicam-hello                # Camera preview (should open)
rpicam-still -o test.jpg    # Capture image
aplay -l                    # List audio devices
speaker-test -c2            # Speaker test
```
Network
``` bash
ip a                        # IP addresses
ping 8.8.8.8                # Internet test
ss -ltn                     # Listening TCP ports
curl http://localhost:8000/state   # Robot state (JSON)
curl http://localhost:8000/health  # Robot health
```
Git
``` bash
git status
git diff
git log --oneline --graph
git pull
git push
```
Python
``` bash
python -V
pip list
python -m robot.startup.main
python -m robot.api.server
```
Spy Turtle
``` bash
./scripts/start_turtle.sh
./scripts/stop_turtle.sh
tail -100 logs/log
```
Troubleshooting Order
``` text
1. vcgencmd get_throttled     -> 0x0 expected
2. vcgencmd measure_temp      -> <80°C
3. i2cdetect -y 1             -> 2d 3c 3d visible
4. gpioinfo                   -> check GPIO ownership
5. dmesg | tail -100          -> kernel errors
6. journalctl -xe             -> system errors
7. tail -100 logs/log         -> Spy Turtle logs
8. curl localhost:8000/health -> API OK
9. rpicam-hello               -> camera OK
10. aplay -l                  -> MAX98357A visible
```