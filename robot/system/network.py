import socket
import subprocess


def _run(*command):
    try:return subprocess.run(command,capture_output=True,text=True,timeout=2,check=False).stdout.strip()
    except Exception:return ""


def wifi_ssid():
    value=_run("nmcli","-t","-f","active,ssid","device","wifi")
    for line in value.splitlines():
        if line.startswith("yes:"):return line.split(":",1)[1].replace("\\:",":") or None
    return None


def ip_address():
    value=_run("hostname","-I")
    addresses=[item for item in value.split() if not item.startswith("127.") and ":" not in item]
    if addresses:return addresses[0]
    try:
        with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8",80))
            return sock.getsockname()[0]
    except OSError:return None


def network_status(): return {"ssid":wifi_ssid(),"ip_address":ip_address()}
