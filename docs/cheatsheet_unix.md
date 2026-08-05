Unix Cheat Sheet
Files
``` bash
pwd                      # Current directory
ll                       # Detailed listing
tree -L 2                # Directory tree
find . -name "*.py"      # Find files
find . -type f | wc -l   # Count files
grep -R "text" .         # Search recursively
grep -n "text" file      # Show line numbers
cat file
less file
head -20 file
tail -20 file
tail -f logs/log         # Follow log live
du -sh .
df -h
```
Processes
``` bash
ps aux
pgrep -af python
top
htop
kill PID
pkill -f robot
```
System
``` bash
hostnamectl
uptime
free -h
lsblk
mount
vcgencmd measure_temp    # <80°C
vcgencmd get_throttled   # expect 0x0
```
GPIO / Hardware
``` bash
gpioinfo                 # GPIO ownership
pinctrl                  # Pin functions
i2cdetect -y 1           # expect: 2d 3c 3d
i2cget -y 1 0x2d 0x00
ls /dev/spi*
ls /dev/leds0
dmesg | tail -100
journalctl -xe
```
Camera / Audio
``` bash
rpicam-hello
rpicam-still -o test.jpg
aplay -l                 # MAX98357A should appear
speaker-test -c2
```
Network
``` bash
hostname
hostname -I              # local IP
ip a                     # interfaces
ip r                     # routes
ping spyturtle.local
ping 8.8.8.8
arp -a
ss -ltn
ss -tulpn
curl http://localhost:8000/state
curl http://localhost:8000/health
curl http://localhost:8000/assets
wget http://localhost:8000/state -O -
```
Wi-Fi
``` bash
nmcli device wifi list                     # scan
nmcli device wifi connect "SSID" password "PASSWORD"
nmcli connection show                      # saved networks
nmcli connection delete "SSID"
nmcli device status
iw dev wlan0 link                          # current AP
```
Services / Auto-start
``` bash
systemctl status spy_turtle.service
systemctl start spy_turtle.service
systemctl stop spy_turtle.service
systemctl restart spy_turtle.service
systemctl enable spy_turtle.service        # start on boot
systemctl disable spy_turtle.service
journalctl -u spy_turtle.service -f        # live logs
systemctl status ssh
systemctl status avahi-daemon
```
Git
``` bash
git status
git diff
git log --oneline --graph
git branch
git pull
git push
```
Python
``` bash
python -V
which python
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
1. vcgencmd get_throttled      -> expect 0x0
2. vcgencmd measure_temp       -> <80°C
3. hostname -I                 -> IP assigned
4. ping spyturtle.local        -> reachable
5. i2cdetect -y 1              -> 2d 3c 3d
6. gpioinfo                    -> GPIO ownership OK
7. dmesg | tail -100
8. journalctl -xe
9. tail -100 logs/log
10. curl localhost:8000/health -> API OK
11. rpicam-hello               -> camera OK
12. aplay -l                   -> audio device visible
```