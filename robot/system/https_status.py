import socket,ssl,subprocess
from urllib.request import Request,urlopen
def active(name):return subprocess.run(["systemctl","is-active",name],capture_output=True,text=True,timeout=3,check=False).stdout.strip()=="active"
def port_open(port):
    try:
        with socket.create_connection(("127.0.0.1",port),2):return True
    except OSError:return False
def proxy_status():
    try:
        with urlopen(Request("https://127.0.0.1/health",headers={"Host":"spyturtle.local"}),context=ssl._create_unverified_context(),timeout=4) as response:return response.status
    except Exception:return None
def get_https_status():return {"caddy_active":active("caddy"),"port_443":port_open(443),"proxy_http_status":proxy_status()}
